CONFIG = {
    "preset": "chess",
    "camera_index": 0,
    "width": 1280,
    "height": 720,
    "fps": 30,
    "process_fps": 30,
    "mirror": True,
    "window_name": "AHOGADO ArUco Viewer",
    # OpenCV ArUco dictionary constant name.
    "aruco_dictionary": "DICT_4X4_50",
    # Keep IDs in the common 4x4_50 range.
    "max_id": 8,
    "min_size_px": 25,
    "blur": 0,
    "denoise": 0,
    "equalize_hist": False,
    "refine_corners": False,
    "pos_alpha": 0.28,
    "size_alpha": 0.25,
    "angle_alpha": 0.22,
    "max_missed_frames": 3,
    "show_timing": True,

    # For interpolation of missing marker detection. Going from last value to new in x seconds
    "interpolation_min": 2,
    # id is considered lost after this many seconds of not being detected, even with interpolation
    "interpolation_timeout":5,
    "phantom_decay": True,

    # OSC output
    "osc_host": "127.0.0.1",
    "osc_port": 9000,
    # Minimum change in any parameter before re-sending (0.0 = always send)
    "osc_dead_zone": 0.002,
}
