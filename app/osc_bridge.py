from typing import Dict, List, Optional

from pythonosc import udp_client


def open_osc_client(host: str, port: int) -> udp_client.SimpleUDPClient:
    return udp_client.SimpleUDPClient(host, port)


def average_duplicate_markers(markers: List[Dict]) -> List[Dict]:
    """Average position/angle/size for markers sharing the same ID."""
    grouped: Dict[int, List[Dict]] = {}
    for m in markers:
        grouped.setdefault(m["id"], []).append(m)

    result = []
    for marker_id, group in grouped.items():
        if len(group) == 1:
            result.append(group[0])
            continue

        avg_x = sum(m["center"][0] for m in group) / len(group)
        avg_y = sum(m["center"][1] for m in group) / len(group)
        avg_size = sum(m["size"] for m in group) / len(group)

        # Circular average for angle (handles 0/360 wraparound)
        import math
        sin_sum = sum(math.sin(math.radians(m["angle"])) for m in group)
        cos_sum = sum(math.cos(math.radians(m["angle"])) for m in group)
        avg_angle = math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0

        avg_health = sum(m.get("health", 1.0) for m in group) / len(group)

        result.append({
            "id": marker_id,
            "center": (avg_x, avg_y),
            "size": avg_size,
            "angle": avg_angle,
            "health": avg_health,
            "phantom": all(m.get("phantom", False) for m in group),
            "corners": group[0]["corners"],
        })

    return result


def send_marker(
    client: udp_client.SimpleUDPClient,
    marker_id: int,
    x_norm: float,
    y_norm: float,
    angle: float,
    size: float,
    health: float,
    send_state: Dict,
    dead_zone: float,
    address: Optional[str] = None,
) -> None:
    """Send an OSC message for a marker if any value changed beyond dead_zone.

    ``address`` is the full OSC path to use. Falls back to ``/aruco/{id}``
    when not supplied (e.g. when running without a preset).
    """
    key = str(marker_id)
    current = (x_norm, y_norm, angle, size, health)
    last = send_state.get(key)

    if last is None or any(abs(c - l) >= dead_zone for c, l in zip(current, last)):
        send_state[key] = current
        osc_address = address if address is not None else f"/aruco/{marker_id}"
        client.send_message(osc_address, list(current))
