import logging
from pathlib import Path

import numpy as np
import plyfile
import rerun as rr
import torch
import trimesh

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def resize_image_and_depth(
    width: int,
    height: int,
    intrinsics: torch.Tensor,
    image: torch.Tensor,
    depth: torch.Tensor | None,
    maximum_long_edge: int,
) -> tuple[int, int, torch.Tensor, torch.Tensor, torch.Tensor | None]:
    """
    Resize the image and depth map while preserving their aspect ratio.
    The longer edge of the resized images will be equal to maximum_long_edge.
    Args:
        width (int): Original width of the image.
        height (int): Original height of the image.
        intrinsics (torch.Tensor): 3x3 tensor representing the camera intrinsics.
        image (torch.Tensor): 3xHxW tensor representing the image.
        depth (torch.Tensor): HxW tensor representing the depth map.
        maximum_long_edge (int): Maximum length of the longer edge after resizing.
    Returns:
        new_width (int): Width of the resized image.
        new_height (int): Height of the resized image.
        new_intrinsics (torch.Tensor): Resized camera intrinsics.
        resized_image (torch.Tensor): Resized image.
        resized_depth (torch.Tensor | None): Resized depth map or None.
    """

    if maximum_long_edge > max((width, height)):
        raise RuntimeError("maximum_long_edge is larger than the longest image edge.")

    # Calculate the aspect ratio of the original image
    aspect_ratio = width / height
    # Determine whether the width or height is the longer edge
    if width > height:
        new_width = maximum_long_edge
        new_height = int(maximum_long_edge / aspect_ratio)
    else:
        new_width = int(maximum_long_edge * aspect_ratio)
        new_height = maximum_long_edge
    # Resize the image and depth map
    # bilinear interpolation
    resized_image = torch.nn.functional.interpolate(
        image.unsqueeze(0),
        size=(new_height, new_width),
        mode="bilinear",
        align_corners=False,
    ).squeeze(0)
    # depth resize with nearest
    resized_depth = (
        None
        if depth is None
        else torch.nn.functional.interpolate(
            depth.unsqueeze(0).unsqueeze(0),
            size=(new_height, new_width),
            mode="nearest",
        )
        .squeeze(0)
        .squeeze(0)
    )

    # Update the camera intrinsics
    scale = new_width / width
    new_intrinsics = intrinsics.clone()
    new_intrinsics[0, 0] *= scale
    new_intrinsics[1, 1] *= scale
    new_intrinsics[0, 2] *= scale
    new_intrinsics[1, 2] *= scale
    return new_width, new_height, new_intrinsics, resized_image, resized_depth


def resize_semantics(
    new_width: int,
    new_height: int,
    semantics: torch.Tensor,
) -> torch.Tensor:
    """
    Resize the image and depth map while preserving their aspect ratio.
    The longer edge of the resized images will be equal to maximum_long_edge.
    Args:
        new_width (int): Resized width of the image.
        new_height (int): Resized height of the image.
        semantics (torch.Tensor): 3xHxW tensor representing the semantics.
    Returns:
        resized_semantics (torch.Tensor): Resized semantics.
    """
    # Resize the semantics (nearest interpolation)
    semantics = semantics.float()
    resized_semantics = (
        torch.nn.functional.interpolate(
            semantics.unsqueeze(0).unsqueeze(0),
            size=(new_height, new_width),
            mode="nearest",
        )
        .squeeze(0)
        .squeeze(0)
    )
    resized_semantics = resized_semantics.int()
    return resized_semantics


def downsample_pc_and_colors(points, colors=None, max_points=None):
    if max_points is not None and max_points > 0 and max_points < len(points):
        # Downsample if needed
        indices = np.arange(0, len(points), len(points) // max_points)
        points = points[indices]
        if colors is not None:
            colors = colors[indices]
    return points, colors


def load_point_cloud_with_colors(file_path, max_points=None):
    """
    Load point cloud with colors from a PLY file.
    Args:
        file_path (str): Path to the PLY file.
    Returns:
        tuple: A tuple containing point coordinates and colors as numpy arrays.
    """
    if file_path.endswith(".ply"):
        with open(file_path, "rb") as f:
            ply_data = plyfile.PlyData.read(f)
            vertex_data = ply_data["vertex"].data
            # Extract point coordinates
            points = np.vstack([vertex_data["x"], vertex_data["y"], vertex_data["z"]]).T
            # Check if color information is available
            if "red" in vertex_data.dtype.names:
                colors = np.vstack(
                    [vertex_data["red"], vertex_data["green"], vertex_data["blue"]]
                ).T
            else:
                colors = None
    elif file_path.endswith(".npy"):
        points = np.load(file_path)
        if Path(
            file_path.replace("global_pts3d.npy", "global_pts3d_colors.npy")
        ).exists():
            # TODO: Adhoc way to also load color, make this more principled and
            # cfg configurable
            colors = np.load(
                file_path.replace("global_pts3d.npy", "global_pts3d_colors.npy")
            )
        else:
            colors = None
    points, colors = downsample_pc_and_colors(points, colors, max_points)
    return points, colors


def log_mesh_to_rerun(path: str | Path):
    # Log this node's mesh, if it has one.
    logger.info(f"Loading scene {path}…")

    mesh = trimesh.load(path, process=False)

    if mesh is not None:
        vertex_colors = None
        vertex_texcoords = None
        albedo_factor = None
        albedo_texture = None

        try:
            vertex_texcoords = mesh.visual.uv
            # trimesh uses the OpenGL convention for UV coordinates, so we need to flip the V coordinate
            # since Rerun uses the Vulkan/Metal/DX12/WebGPU convention.
            vertex_texcoords[:, 1] = 1.0 - vertex_texcoords[:, 1]
        except Exception:
            pass

        try:
            albedo_texture = mesh.visual.material.baseColorTexture
            if mesh.visual.material.baseColorTexture is None:
                raise ValueError()
        except Exception:
            # Try vertex colors instead.
            try:
                colors = np.asarray(mesh.visual.vertex_colors)
                if len(colors) == 4:
                    # If trimesh gives us a single vertex color for the entire mesh, we can interpret that
                    # as an albedo factor for the whole primitive.
                    albedo_factor = np.array(colors)
                else:
                    vertex_colors = colors
            except Exception:
                pass

        rr.log(
            "global_mesh",
            rr.Mesh3D(
                vertex_positions=mesh.vertices,
                vertex_colors=vertex_colors,
                vertex_normals=mesh.vertex_normals,
                vertex_texcoords=vertex_texcoords,
                albedo_texture=albedo_texture,
                triangle_indices=mesh.faces,
                albedo_factor=albedo_factor,
            ),
        )
