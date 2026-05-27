"""Lightweight validation for the tourbox-preset JSON format (no deps).

The JSON document shape::

    {
      "format": "tourbox-preset",
      "schemaVersion": 1,
      "tbVersion": "1.8",        # optional; mirrors <version>, preserved on encode
      "device": "elite",         # optional
      "name": "My Preset",       # optional
      "bindings": {              # button-name (or "0xNN") -> action dict
        "0x10": {"type": "key", "key": "E"},
        ...
      }
    }
"""
from __future__ import annotations

__all__ = ["FORMAT", "SCHEMA_VERSION", "validate", "SchemaError"]

FORMAT = "tourbox-preset"
SCHEMA_VERSION = 1

_ACTION_TYPES = {"none", "raw", "key", "rotary", "mouse", "macro", "builtin", "tourmenu"}


class SchemaError(ValueError):
    pass


def validate(doc: dict) -> None:
    """Raise :class:`SchemaError` if ``doc`` is not a well-formed preset."""
    if not isinstance(doc, dict):
        raise SchemaError("top level must be an object")
    if doc.get("format") != FORMAT:
        raise SchemaError(f'"format" must be {FORMAT!r}')
    if doc.get("schemaVersion") != SCHEMA_VERSION:
        raise SchemaError(f'"schemaVersion" must be {SCHEMA_VERSION}')
    bindings = doc.get("bindings")
    if not isinstance(bindings, dict):
        raise SchemaError('"bindings" must be an object')
    for key, action in bindings.items():
        _validate_action(key, action)


def _validate_action(key: str, action: object) -> None:
    where = f"binding {key!r}"
    if not isinstance(action, dict):
        raise SchemaError(f"{where}: action must be an object")
    t = action.get("type")
    if t not in _ACTION_TYPES:
        raise SchemaError(f"{where}: unknown action type {t!r}")
    if t == "raw" and "hex" not in action:
        raise SchemaError(f"{where}: raw action requires 'hex'")
    if t == "key" and "key" not in action:
        raise SchemaError(f"{where}: key action requires 'key'")
    if t == "mouse" and "action" not in action:
        raise SchemaError(f"{where}: mouse action requires 'action'")
    if t == "rotary":
        has_cw = "cw" in action or "up" in action
        has_ccw = "ccw" in action or "down" in action
        if not (has_cw and has_ccw):
            raise SchemaError(f"{where}: rotary requires two directions (cw/ccw or up/down)")
