import cv2
import numpy as np


def draw_hud(frame, detected_count: int, midi_port_name: str, mirror: bool, paused: bool) -> None:
    signal_color = (0, 220, 0) if detected_count > 0 else (0, 0, 200)
    cv2.circle(frame, (28, 28), 10, signal_color, -1)

    lines = [
        f"Detected: {detected_count}",
        f"MIDI: {midi_port_name if midi_port_name else 'disabled'}",
        "Keys: q=quit z=zero r=reset p=pause u=apply-id-dz m=mirror",
        f"Mirror: {'on' if mirror else 'off'} | {'paused' if paused else 'running'}",
    ]

    y = 24
    for line in lines:
        cv2.putText(
            frame,
            line,
            (50, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (230, 230, 230),
            1,
            cv2.LINE_AA,
        )
        y += 22


def build_sidebar(height: int, width: int, title: str):
    panel = np.zeros((height, width, 3), dtype=np.uint8)
    panel[:, :] = (24, 24, 24)

    cv2.putText(
        panel,
        title,
        (16, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (220, 220, 220),
        2,
        cv2.LINE_AA,
    )
    return panel


def draw_sidebar_status(panel, line: int, label: str, value: str) -> int:
    y = 54 + line * 24
    cv2.putText(panel, f"{label}: {value}", (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.56, (200, 200, 200), 1, cv2.LINE_AA)
    return line + 1


def draw_marker_rows(panel, start_line: int, rows):
    line = start_line
    cv2.putText(panel, "Marker Assignments", (16, 54 + line * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 230, 120), 1, cv2.LINE_AA)
    line += 1
    cv2.putText(panel, "ID | CH | BASE | DZ | X Y A", (16, 54 + line * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (120, 200, 255), 1, cv2.LINE_AA)
    line += 1

    max_rows = max(0, (panel.shape[0] - (54 + line * 24) - 12) // 22)
    for row in rows[:max_rows]:
        text = f"{row['id']:>2} | {row['ch']:>2} | {row['base']:>3} | {row['dz']:>2} | {row['x']:>3} {row['y']:>3} {row['a']:>3}"
        cv2.putText(panel, text, (16, 54 + line * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
        line += 1


def compose_layout(frame, sidebar):
    return np.hstack([frame, sidebar])


def show_window(name: str, frame):
    cv2.imshow(name, frame)


def read_key() -> int:
    return cv2.waitKey(1) & 0xFF


def close_windows() -> None:
    cv2.destroyAllWindows()
