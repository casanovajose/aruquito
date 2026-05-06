import cv2
import time

from aruco_tracker import create_aruco_detector, detect_markers, draw_markers, mirror_markers, preprocess_for_detection
from camera import close_camera, open_camera, read_frame
from config import CONFIG
from osc_bridge import average_duplicate_markers, open_osc_client, send_marker


def lerp_scalar(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount


def update_track_health(track, now: float, interpolation_min: float, interpolation_timeout: float, phantom_decay: bool) -> None:
    if track["detected"]:
        if interpolation_min <= 0.0:
            track["health"] = 1.0
            return

        amount = min(1.0, max(0.0, (now - float(track["health_started_at"])) / interpolation_min))
        track["health"] = lerp_scalar(float(track["health_start"]), 1.0, amount)
        return

    if not phantom_decay or interpolation_timeout <= 0.0:
        track["health"] = float(track["health_start"])
        return

    amount = min(1.0, max(0.0, (now - float(track["phantom_started_at"])) / interpolation_timeout))
    track["health"] = max(0.0, lerp_scalar(float(track["health_start"]), 0.0, amount))


def run() -> int:
    cap = open_camera(CONFIG["camera_index"], CONFIG["width"], CONFIG["height"], CONFIG["fps"])
    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return 1

    detector = create_aruco_detector(CONFIG["aruco_dictionary"], bool(CONFIG.get("refine_corners", False)))
    osc_client = open_osc_client(str(CONFIG["osc_host"]), int(CONFIG["osc_port"]))
    osc_send_state: dict = {}
    osc_dead_zone = float(CONFIG.get("osc_dead_zone", 0.002))
    mirror = bool(CONFIG["mirror"])
    window_name = str(CONFIG["window_name"])
    process_fps = max(1, int(CONFIG.get("process_fps", CONFIG.get("fps", 30))))
    frame_period = 1.0 / float(process_fps)
    show_timing = bool(CONFIG.get("show_timing", False))
    min_size_px = float(CONFIG.get("min_size_px", 0))
    pos_alpha = float(CONFIG.get("pos_alpha", 0.3))
    size_alpha = float(CONFIG.get("size_alpha", 0.25))
    angle_alpha = float(CONFIG.get("angle_alpha", 0.2))
    interpolation_min = max(0.0, float(CONFIG.get("interpolation_min", 0.0)))
    interpolation_timeout = max(0.0, float(CONFIG.get("interpolation_timeout", 0.0)))
    phantom_decay = bool(CONFIG.get("phantom_decay", True))
    tracks = {}

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            loop_start = time.perf_counter()

            t0 = time.perf_counter()
            ok, frame = read_frame(cap)
            if not ok:
                print("ERROR: Camera read failed.")
                break
            t_capture_ms = (time.perf_counter() - t0) * 1000.0

            t1 = time.perf_counter()
            gray = preprocess_for_detection(
                frame,
                int(CONFIG["blur"]),
                int(CONFIG["denoise"]),
                bool(CONFIG.get("equalize_hist", False)),
            )
            t_pre_ms = (time.perf_counter() - t1) * 1000.0

            t2 = time.perf_counter()
            now = t2
            markers = detect_markers(detector, gray)
            markers = [m for m in markers if 0 <= m["id"] <= int(CONFIG["max_id"])]
            markers = [m for m in markers if float(m["size"]) >= min_size_px]
            markers = average_duplicate_markers(markers)

            visible_ids = set()
            for marker in markers:
                marker_id = int(marker["id"])
                visible_ids.add(marker_id)

                track = tracks.get(marker_id)
                if track is None:
                    tracks[marker_id] = {
                        "id": marker_id,
                        "corners": marker["corners"].copy(),
                        "center": marker["center"],
                        "size": float(marker["size"]),
                        "angle": float(marker["angle"]),
                        "detected": True,
                        "health": 0.0 if interpolation_min > 0.0 else 1.0,
                        "health_start": 0.0,
                        "health_started_at": now,
                        "last_seen_at": now,
                        "phantom_started_at": now,
                    }
                    continue

                prev_x, prev_y = track["center"]
                curr_x, curr_y = marker["center"]
                smoothed_center = (
                    (1.0 - pos_alpha) * prev_x + pos_alpha * curr_x,
                    (1.0 - pos_alpha) * prev_y + pos_alpha * curr_y,
                )
                smoothed_size = (1.0 - size_alpha) * track["size"] + size_alpha * float(marker["size"])

                prev_angle = float(track["angle"])
                curr_angle = float(marker["angle"])
                delta_angle = ((curr_angle - prev_angle + 180.0) % 360.0) - 180.0
                smoothed_angle = (prev_angle + angle_alpha * delta_angle) % 360.0

                track["center"] = smoothed_center
                track["size"] = smoothed_size
                track["angle"] = smoothed_angle
                track["corners"] = marker["corners"].copy()
                track["last_seen_at"] = now
                if not track["detected"]:
                    track["detected"] = True
                    track["health_start"] = float(track["health"])
                    track["health_started_at"] = now

            stale_ids = []
            for marker_id, track in tracks.items():
                if marker_id not in visible_ids:
                    if track["detected"]:
                        track["detected"] = False
                        track["health_start"] = float(track["health"])
                        track["phantom_started_at"] = now
                    if (now - float(track["last_seen_at"])) > interpolation_timeout:
                        stale_ids.append(marker_id)

                update_track_health(track, now, interpolation_min, interpolation_timeout, phantom_decay)

            for marker_id in stale_ids:
                tracks.pop(marker_id, None)

            frame_w = float(frame.shape[1])
            frame_h = float(frame.shape[0])
            markers = []
            for marker_id, track in sorted(tracks.items()):
                cx, cy = track["center"]
                health = float(track.get("health", 1.0))
                x_norm = max(0.0, min(1.0, cx / frame_w))
                y_norm = max(0.0, min(1.0, cy / frame_h))
                send_marker(
                    osc_client, marker_id,
                    x_norm, y_norm,
                    float(track["angle"]),
                    float(track["size"]),
                    health,
                    osc_send_state,
                    osc_dead_zone,
                )
                markers.append({
                    "id": marker_id,
                    "corners": track["corners"],
                    "center": track["center"],
                    "size": track["size"],
                    "angle": track["angle"],
                    "phantom": not bool(track.get("detected", False)),
                    "health": health,
                })
            t_detect_ms = (time.perf_counter() - t2) * 1000.0

            t3 = time.perf_counter()
            display_frame = cv2.flip(frame, 1) if mirror else frame.copy()
            display_markers = mirror_markers(markers, frame.shape[1]) if mirror else markers

            draw_markers(display_frame, display_markers)
            cv2.putText(
                display_frame,
                f"Detected: {len(display_markers)} | q:quit m:mirror",
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (220, 220, 220),
                2,
                cv2.LINE_AA,
            )
            t_draw_ms = (time.perf_counter() - t3) * 1000.0

            total_ms = (time.perf_counter() - loop_start) * 1000.0
            if show_timing:
                cv2.putText(
                    display_frame,
                    f"ms cap:{t_capture_ms:.1f} pre:{t_pre_ms:.1f} det:{t_detect_ms:.1f} draw:{t_draw_ms:.1f} total:{total_ms:.1f}",
                    (12, 56),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (180, 255, 180),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow(window_name, display_frame)

            sleep_left = frame_period - (time.perf_counter() - loop_start)
            wait_ms = 1 if sleep_left <= 0 else max(1, int(sleep_left * 1000.0))
            key = cv2.waitKey(wait_ms) & 0xFF
            if key == ord("q"):
                break
            if key == ord("m"):
                mirror = not mirror
    finally:
        close_camera(cap)
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
