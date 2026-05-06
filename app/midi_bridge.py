from typing import Dict, Optional

import mido


def list_output_ports():
    return mido.get_output_names()


def open_output_port(port_name: str):
    ports = list_output_ports()
    if not ports:
        return None

    if port_name:
        if port_name not in ports:
            raise ValueError(f"MIDI output port not found: {port_name}")
        return mido.open_output(port_name)

    return mido.open_output(ports[0])


def clamp_midi(value: float) -> int:
    return max(0, min(127, int(round(value))))


def to_midi_7bit(normalized: float) -> int:
    return clamp_midi(normalized * 127.0)


def base_cc_for_id(marker_id: int, base_cc_id0: int) -> int:
    return base_cc_id0 + marker_id * 3


def send_cc(port, channel_1_to_16: int, cc: int, value: int) -> None:
    if port is None:
        return

    channel = max(1, min(16, channel_1_to_16)) - 1
    msg = mido.Message("control_change", channel=channel, control=int(cc), value=int(value))
    port.send(msg)


def should_send(state: Dict, key: str, current_value: int, dead_zone: int) -> bool:
    last = state.get(key)
    if last is None:
        state[key] = current_value
        return True

    if abs(current_value - last) >= dead_zone:
        state[key] = current_value
        return True

    return False


def send_marker_triplet(
    port,
    marker_id: int,
    channel: int,
    base_cc_id0: int,
    x_midi: int,
    y_midi: int,
    a_midi: int,
    send_state: Dict,
    dead_zone: int,
) -> None:
    cc0 = base_cc_for_id(marker_id, base_cc_id0)
    keys = {
        "x": f"{marker_id}:x",
        "y": f"{marker_id}:y",
        "a": f"{marker_id}:a",
    }

    if should_send(send_state, keys["x"], x_midi, dead_zone):
        send_cc(port, channel, cc0, x_midi)
    if should_send(send_state, keys["y"], y_midi, dead_zone):
        send_cc(port, channel, cc0 + 1, y_midi)
    if should_send(send_state, keys["a"], a_midi, dead_zone):
        send_cc(port, channel, cc0 + 2, a_midi)
