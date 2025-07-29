# Example usage:
# in another terminal start a Rerun server:
# RUST_LOG=info rerun --serve-web --port 9081 --ws-server-port 9082 --web-viewer-port 9083
# and make sure the ws-server-port and web-viewer-port are forwarded to your local
# machine if this runs on a remote machine.
# If developing locally, you can also just use: rerun --port 9081

# Example usage:
# python -m  wai.viz.visualize_wai ~/code/wai/wai/configs/debug_visualize/debug_undistort.yaml root=/home/duncanzauss/eyeful_dummy_wai every_nth_sample=132 n_samples=8 global_pc_path=/home/duncanzauss/eyeful_dummy_wai/table/point_cloud.ply
# python -m  wai.viz.visualize_wai ~/code/wai/wai/configs/debug_visualize/debug_viz_final.yaml root=~/dryrun/scannetppv2 every_nth_sample=60 n_samples=3 depth_name="pred_depth"
import logging

import numpy as np
import rerun as rr
import torch
from argconf import argconf_parse

from wai import WAI_CONFIG_PATH
from wai.utils import get_scene_frame_names
from wai.utils.io import _load_labeled_mesh
from wai.utils.m_ops import m_unproject
from wai.utils.semantics import apply_id_to_color_mapping, load_semantic_color_mapping
from wai.utils.viz_utils import (
    downsample_pc_and_colors,
    load_point_cloud_with_colors,
    log_mesh_to_rerun,
    resize_image_and_depth,
    resize_semantics,
)
from wai.wai_dataset import WaiSceneframeDataset

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def visualize_wai_with_rerun(cfg):
    if cfg.scene_id:
        # Add filter to the first position as this filter is the fastest one
        cfg.scene_filters.insert(0, [cfg.scene_id])

    ### Config and dataset setup ###
    scene_frame_names = get_scene_frame_names(cfg)
    enabled_semantics_visualization = cfg.visualize_semantics in [
        "semantic_class",
        "instance",
    ]
    if enabled_semantics_visualization:
        semantic_color_mapping = load_semantic_color_mapping()

    if len(scene_frame_names) == 0:
        raise RuntimeError(
            f"No scenes found in {cfg.root} that fulfill the scene filters: {cfg.scene_filters}"
        )
    logger.info(f"Found {len(scene_frame_names)} scenes in {cfg.root}")
    if not cfg.scene_id:
        # Just take the first scene if nothing specified
        cfg["scene_id"] = list(scene_frame_names.keys())[0]
    else:
        cfg["scene_id"] = str(cfg.scene_id)
    if cfg.scene_id not in scene_frame_names:
        raise ValueError(
            f"Specified to visualize scene {cfg.scene_id}, but this scene does not exist in {cfg.root}"
        )
    cfg.scene_filters = [cfg.scene_id]
    single_scene_dataset = WaiSceneframeDataset(cfg)
    if (
        cfg.every_nth_sample > 0
        and len(single_scene_dataset) < cfg.every_nth_sample * cfg.n_samples
    ):
        raise RuntimeError(
            "Specified visualization indices out of bounds for this scene"
        )

    ### Rerun setup ###
    if cfg.rr_local_developement:
        # Locally: Just create a new rerun server
        rr.init(application_id=cfg.rr_session_name, strict=True, spawn=True)
    else:
        # Remote: Forward all the logged data to a running server at the specified IP:Port
        rr.init(application_id=cfg.rr_session_name, strict=True, spawn=False)
        rr.connect_tcp(cfg.rr_address)

    # Log world coordinate system
    rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_UP, static=True)  # Set an up-axis
    rr.log(
        "world/xyz",
        rr.Arrows3D(
            vectors=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            colors=[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        ),
    )

    # Log global PC if any
    if cfg.global_pc_path is not None:
        points, colors = load_point_cloud_with_colors(
            cfg.global_pc_path, cfg.max_global_points
        )
        rr.log("global_point_cloud", rr.Points3D(points, colors=colors))

    # Log mesh if any
    if cfg.visualize_mesh and cfg.global_mesh_path is not None:
        if not enabled_semantics_visualization:
            # standard mesh visualization
            log_mesh_to_rerun(cfg.global_mesh_path)
        else:
            # labeled mesh visualization
            labeled_mesh = _load_labeled_mesh(cfg.global_mesh_path, fmt="np")

            # select semantic colors (class or instance)
            vertex_colors = labeled_mesh[f"vertices_{cfg.visualize_semantics}_color"]

            # log to rerun
            rr.log(
                "labeled_mesh",
                rr.Mesh3D(
                    vertex_positions=np.asarray(labeled_mesh["vertices"]),
                    vertex_colors=np.asarray(vertex_colors),
                    triangle_indices=np.asarray(labeled_mesh["faces"]),
                ),
            )

    for sample_idx in range(
        0,
        (
            cfg.n_samples * cfg.every_nth_sample
            if cfg.n_samples > 0
            else len(single_scene_dataset)
        ),
        cfg.every_nth_sample,
    ):
        sample = single_scene_dataset[sample_idx]
        if sample["camera_model"] != "PINHOLE":
            if cfg.get("treat_any_camera_as_pinhole", False):
                # TODO: Implement proper support for distorted images
                logger.warning(
                    "The camera model is not pinhole, but the visualizer "
                    "treats it as pinhole."
                )
            else:
                raise NotImplementedError(
                    "The rerun-based visualitzation tool only supports pinhole cameras."
                    "Consider adding the flag treat_any_camera_as_pinhole=True to "
                    "visualize the distorted images anyway."
                )
        ### Actual logging of the data ###
        # Remove all / from the name as they are used in rerun to describe parent/child relationships
        base_name = f"view_{sample['scene_name']}_{sample['frame_name']}".replace(
            "/", "_"
        )
        logger.info(f"Logging {base_name}.")
        width, height = sample["w"], sample["h"]
        pose = sample["extrinsics"]
        intrinsics = sample["intrinsics"]
        image_torch = sample["image"]
        depth_raw: torch.Tensor | None = (
            sample[cfg.depth_name] if cfg.visualize_depth else None
        )
        if (
            depth_raw is not None
            and len(depth_raw.shape) == 3
            and depth_raw.shape[0] == 3
        ):
            # Short term fix for wrongly loaded depth map with size [3, W, H] where it should be [W, H]
            # TODO (normanm, duncanzauss): Investigate why depth is wrongly loaded here
            depth_raw = depth_raw[0, ...]
        if depth_raw is not None and (
            width / height < depth_raw.shape[1] / depth_raw.shape[0] * 0.99
            or width / height > depth_raw.shape[1] / depth_raw.shape[0] * 1.01
        ):
            raise RuntimeError(
                f"Image aspect ratio mismatched: Image size of {width},{height} "
                f"and depth map size of {depth_raw.shape[1]}, {depth_raw.shape[0]}."
            )
        if cfg.max_viz_long_edge > 0:
            width, height, intrinsics, image_torch, depth_map = resize_image_and_depth(
                width=width,
                height=height,
                intrinsics=intrinsics,
                image=image_torch,
                depth=depth_raw,
                maximum_long_edge=cfg.max_viz_long_edge,
            )
            logger.info(
                f"Resized intrinsics, depth map and image with the specified "
                f"long edge of {cfg.max_viz_long_edge} to size {width}, "
                f"{height}."
            )
        elif depth_raw is not None and depth_raw.shape[0] != height:
            logger.info("Resizing the depth map to image size.")
            depth_map = (
                torch.nn.functional.interpolate(
                    depth_raw.unsqueeze(0).unsqueeze(0),
                    size=(image_torch.shape[-2:]),
                    mode="nearest",
                )
                .squeeze(0)
                .squeeze(0)
            )
        else:
            depth_map = depth_raw

        if not enabled_semantics_visualization:
            image = (image_torch.permute((1, 2, 0)) * 255.0).to(
                dtype=torch.uint8, device="cpu"
            )
            rr.log(
                base_name,
                rr.Transform3D(
                    translation=pose[:3, 3],
                    mat3x3=pose[:3, :3],
                    from_parent=False,
                ),
            )
            rr.log(
                f"{base_name}/pinhole",
                rr.Pinhole(
                    image_from_camera=intrinsics,
                    height=height,
                    width=width,
                    # RDF -->X right, Y down, Z forward
                    camera_xyz=rr.ViewCoordinates.RDF,
                    image_plane_distance=0.2,
                ),
            )
            # TODO: Add anon masking when logging the image??
            rr.log(f"{base_name}/pinhole/rgb", rr.Image(image))

        if cfg.visualize_depth:
            if cfg.colorized_depth:
                # TODO (duncanzauss): Investigate if rerun can directly colorize the depth map i.e. with rr.DepthImage
                pts_xyz = m_unproject(
                    depth_map,
                    intrinsics,
                    cam2world=pose,
                    H=height,
                    W=width,
                )
                pts_color = image.flatten(0, 1)
                pts_xyz, pts_color = downsample_pc_and_colors(
                    pts_xyz, pts_color, cfg.max_col_points_per_view
                )
                rr.log(
                    # TODO: Need to find a way
                    f"depth_colorized_{sample['scene_name']}_{sample['frame_name']}",
                    rr.Points3D(
                        pts_xyz,
                        colors=pts_color,
                        radii=float(cfg.get("colored_viz_radii", 0.01)),
                    ),
                )
            else:
                rr.log(
                    f"{base_name}/pinhole/depth",
                    rr.DepthImage(depth_map, point_fill_ratio=0.1, colormap="turbo"),
                )

        if enabled_semantics_visualization:
            # load the semantics from the scene
            semantics_key = f"rendered_{cfg.visualize_semantics}"
            semantic_ids = sample[semantics_key]
            semantic_ids = resize_semantics(width, height, semantic_ids)
            semantic_colors_image, _ = apply_id_to_color_mapping(
                semantic_ids, semantic_color_mapping
            )

            # upload camera and labeled_image to rerun
            rr.log(
                base_name,
                rr.Transform3D(
                    translation=pose[:3, 3],
                    mat3x3=pose[:3, :3],
                    from_parent=False,
                ),
            )
            rr.log(
                f"{base_name}/pinhole",
                rr.Pinhole(
                    image_from_camera=intrinsics,
                    height=height,
                    width=width,
                    # RDF -->X right, Y down, Z forward
                    camera_xyz=rr.ViewCoordinates.RDF,
                    image_plane_distance=0.2,
                ),
            )
            rr.log(
                f"{base_name}/pinhole/{cfg.visualize_semantics}",
                rr.Image(semantic_colors_image),
            )


if __name__ == "__main__":
    conf = argconf_parse(
        str(WAI_CONFIG_PATH / "debug_visualize" / "debug_viz_final.yaml")
    )
    if conf.visualizer == "rerun":
        visualize_wai_with_rerun(conf)
    elif conf.visualizer == "dvis":
        # TODO: implement
        raise NotImplementedError("dvis visualizer not yet implemented for wai")
    else:
        raise RuntimeError(f"Unsupported visualizer {conf.visualizer}")
