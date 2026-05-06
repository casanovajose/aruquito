import cv2


DEFAULT_CONTROL_WINDOW = "AHOGADO Python ArUco"


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def _noop(_):
    return None


def create_controls(
    window_name: str,
    initial_ids: int,
    initial_dead_zone: int,
    initial_blur: int,
    initial_denoise: int,
    initial_process_fps: int,
) -> None:
    control_window = window_name or DEFAULT_CONTROL_WINDOW

    cv2.createTrackbar("IDs", control_window, clamp_int(initial_ids, 1, 32), 32, _noop)
    cv2.createTrackbar("Global DZ", control_window, clamp_int(initial_dead_zone, 0, 32), 32, _noop)
    cv2.createTrackbar("Blur", control_window, clamp_int(initial_blur, 0, 10), 10, _noop)
    cv2.createTrackbar("Denoise", control_window, clamp_int(initial_denoise, 0, 20), 20, _noop)
    cv2.createTrackbar("Proc FPS", control_window, clamp_int(initial_process_fps, 5, 60), 60, _noop)
    cv2.createTrackbar("Edit ID", control_window, 0, 31, _noop)
    cv2.createTrackbar("ID DZ", control_window, clamp_int(initial_dead_zone, 0, 32), 32, _noop)


def read_controls(window_name: str):
    control_window = window_name or DEFAULT_CONTROL_WINDOW

    ids = max(1, cv2.getTrackbarPos("IDs", control_window))
    global_dead_zone = cv2.getTrackbarPos("Global DZ", control_window)
    blur = cv2.getTrackbarPos("Blur", control_window)
    denoise = cv2.getTrackbarPos("Denoise", control_window)
    process_fps = max(5, cv2.getTrackbarPos("Proc FPS", control_window))
    edit_id = cv2.getTrackbarPos("Edit ID", control_window)
    id_dead_zone = cv2.getTrackbarPos("ID DZ", control_window)

    return {
        "ids": ids,
        "global_dead_zone": global_dead_zone,
        "blur": blur,
        "denoise": denoise,
        "process_fps": process_fps,
        "edit_id": edit_id,
        "id_dead_zone": id_dead_zone,
    }
