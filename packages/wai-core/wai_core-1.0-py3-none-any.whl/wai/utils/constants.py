PINHOLE_CAM_KEYS = ["fl_x", "fl_y", "cx", "cy", "h", "w"]
DISTORTION_PARAM_KEYS = [
    "k1",
    "k2",
    "k3",
    "k4",
    "p1",
    "p2",
]  # order corresponds to the OpenCV convention
CAMERA_KEYS = PINHOLE_CAM_KEYS + DISTORTION_PARAM_KEYS
