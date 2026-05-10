"""
Preset loader — imports a preset module by name and exposes a normalised interface.

Each preset module must define:
    MARKER_IDS  : set[int]        — valid marker IDs for this preset
    OSC_PREFIX  : dict[int, str]  — marker_id -> OSC address (e.g. "/chess/pawn/white")
    MARKER_LABELS: dict[int, str] — marker_id -> human-readable label (optional but encouraged)

If no preset is configured (name is None / empty), a NullPreset is returned that
accepts all IDs and uses the generic "/aruco/{id}" address scheme.
"""

import importlib
import types
from typing import Optional


class _NullPreset:
    """Fallback when no preset is configured: accept any ID, generic OSC path."""

    MARKER_IDS: set = set()           # empty = accept all
    MARKER_LABELS: dict = {}
    OSC_PREFIX: dict = {}

    def get_address(self, marker_id: int) -> str:
        return f"/aruco/{marker_id}"

    def is_valid(self, marker_id: int) -> bool:
        return True  # no filtering

    def label(self, marker_id: int) -> str:
        return str(marker_id)


class _Preset:
    """Wrapper around a loaded preset module."""

    def __init__(self, module: types.ModuleType) -> None:
        self._module = module
        self.MARKER_IDS: set = getattr(module, "MARKER_IDS", set())
        self.OSC_PREFIX: dict = getattr(module, "OSC_PREFIX", {})
        self.MARKER_LABELS: dict = getattr(module, "MARKER_LABELS", {})

    def get_address(self, marker_id: int) -> str:
        return self.OSC_PREFIX.get(marker_id, f"/aruco/{marker_id}")

    def is_valid(self, marker_id: int) -> bool:
        return marker_id in self.MARKER_IDS

    def label(self, marker_id: int) -> str:
        return self.MARKER_LABELS.get(marker_id, str(marker_id))


def load_preset(name: Optional[str]):
    """
    Load a preset by name and return a _Preset (or _NullPreset if name is falsy).

    The module is looked up as ``presets.<name>`` (relative to the app package).
    """
    if not name:
        return _NullPreset()

    try:
        module = importlib.import_module(f"presets.{name}")
        return _Preset(module)
    except ModuleNotFoundError as exc:
        raise ValueError(f"Preset '{name}' not found in app/presets/: {exc}") from exc
