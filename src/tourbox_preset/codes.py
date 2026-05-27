"""Lookup tables: button codes, key codes, modifier bits, mouse actions.

Most of these were confirmed by the calibration pass (see docs/calibration.md):
controlled exports from TourBox Console diffed against a blank baseline. Entries
that are still unconfirmed are intentionally absent so decoding falls back to
lossless ``raw`` hex rather than guessing.

Payload layout (0-based offsets within the 12-byte payload)::

    [0] action type   : 0x00 single action, 0x08 two-way (rotary turn)
    [1] aux flag       : 0 for the forms we decode (nonzero -> raw, e.g. drag)
    [2..6] sub-action A: [mod, category, _, _, keycode]
    [7..11] sub-action B: [mod, category, _, _, keycode]   (rotary 2nd direction)

    category: 0 = normal key, 1 = extended key (arrows/F-keys), 2 = mouse action
    mod bits: Win=0x01, Shift=0x02, Alt=0x04, Ctrl=0x08
"""
from __future__ import annotations

__all__ = [
    "ELITE_BUTTONS", "button_name", "button_code",
    "MODS", "mods_to_bits", "bits_to_mods",
    "CAT_KEY", "CAT_EXT", "CAT_MOUSE",
    "resolve_key", "key_label",
    "MOUSE", "mouse_name",
]

# ---------------------------------------------------------------------------
# Button code -> Elite button name  (confirmed by calibration round 1-3)
# ---------------------------------------------------------------------------
ELITE_BUTTONS: dict[str, int] = {
    # tool buttons
    "tall": 0x00, "side": 0x01, "top": 0x02, "short": 0x03,
    # d-pad
    "up": 0x10, "down": 0x11, "left": 0x12, "right": 0x13,
    # assisting
    "c1": 0x22, "c2": 0x23, "tour": 0x2A,
    # rotary turns (two-direction) and presses
    "knob": 0x04, "knob_press": 0x37,
    "scroll": 0x09, "scroll_press": 0x0A,
    "dial": 0x0F, "dial_press": 0x38,
}
_BUTTON_BY_CODE = {code: name for name, code in ELITE_BUTTONS.items()}


def button_name(code: int) -> str:
    """Friendly button name for a code, or ``0xNN`` if not yet mapped."""
    return _BUTTON_BY_CODE.get(code, f"0x{code:02X}")


def button_code(name: str) -> int:
    """Inverse of :func:`button_name`. Accepts a name or ``0xNN`` literal."""
    if name in ELITE_BUTTONS:
        return ELITE_BUTTONS[name]
    s = name.strip().lower()
    if s.startswith("0x"):
        return int(s, 16)
    raise KeyError(f"unknown button {name!r}")


# ---------------------------------------------------------------------------
# Modifiers (payload byte 2 bitmask) -- confirmed by calibration round 2
# ---------------------------------------------------------------------------
MODS: dict[str, int] = {"win": 0x01, "shift": 0x02, "alt": 0x04, "ctrl": 0x08}
_MOD_ORDER = ["ctrl", "shift", "alt", "win"]  # canonical output order


def mods_to_bits(mods: list[str]) -> int:
    bits = 0
    for m in mods:
        bits |= MODS[m.lower()]
    return bits


def bits_to_mods(bits: int) -> list[str]:
    """Return modifier names for ``bits``, or raise if an unknown bit is set."""
    known = 0
    for v in MODS.values():
        known |= v
    if bits & ~known:
        raise ValueError(f"unknown modifier bits {bits:#04x}")
    return [m for m in _MOD_ORDER if bits & MODS[m]]


# ---------------------------------------------------------------------------
# Key codes (payload byte 6), split by category (payload byte 3)
# ---------------------------------------------------------------------------
CAT_KEY = 0
CAT_EXT = 1
CAT_MOUSE = 2

# Normal keys (category 0). Confirmed: letters/digits/space + the named control
# keys and punctuation seen in real presets.
_NORMAL_NAME2CODE: dict[str, int] = {}
for _b in range(ord("A"), ord("Z") + 1):
    _NORMAL_NAME2CODE[chr(_b)] = _b
for _b in range(ord("0"), ord("9") + 1):
    _NORMAL_NAME2CODE[chr(_b)] = _b
_NORMAL_NAME2CODE.update({
    "Space": 0x20, "Tab": 0x09, "Enter": 0x0D, "Esc": 0x1B,
    "Backspace": 0x08, "Delete": 0x7F,
})
for _ch in "[]+-=,./;'`\\":
    _NORMAL_NAME2CODE[_ch] = ord(_ch)

# Extended keys (category 1). Only calibration-confirmed entries.
# ▶ TBD: remaining arrows (Left/Right) and F2-F12 need another calibration round.
_EXT_NAME2CODE: dict[str, int] = {
    "ArrowUp": 0x01, "ArrowDown": 0x02, "F1": 0x0A,
}

_NORMAL_CODE2NAME = {v: k for k, v in _NORMAL_NAME2CODE.items()}
_EXT_CODE2NAME = {v: k for k, v in _EXT_NAME2CODE.items()}


def resolve_key(name: str) -> tuple[int, int]:
    """Return ``(category, keycode)`` for a key name. Single chars map to ASCII."""
    if name in _EXT_NAME2CODE:
        return CAT_EXT, _EXT_NAME2CODE[name]
    if name in _NORMAL_NAME2CODE:
        return CAT_KEY, _NORMAL_NAME2CODE[name]
    if len(name) == 1:
        return CAT_KEY, ord(name)
    raise KeyError(f"unknown key {name!r}")


def key_label(category: int, code: int) -> str | None:
    """Return the key name for a (category, code), or ``None`` if unconfirmed."""
    if category == CAT_KEY:
        return _NORMAL_CODE2NAME.get(code)
    if category == CAT_EXT:
        return _EXT_CODE2NAME.get(code)
    return None


# ---------------------------------------------------------------------------
# Mouse actions (category 2, code at byte 6) -- confirmed calibration round 3
# ▶ TBD: mouse drag (uses type 0x08 with extra bytes) still decodes as raw.
# ---------------------------------------------------------------------------
MOUSE: dict[str, int] = {
    "left": 0x01, "right": 0x02, "middle": 0x03,
    "wheel_up": 0x04, "wheel_down": 0x05, "double": 0x06,
}
_MOUSE_BY_CODE = {v: k for k, v in MOUSE.items()}


def mouse_name(code: int) -> str | None:
    return _MOUSE_BY_CODE.get(code)


# ---------------------------------------------------------------------------
# Built-in features: numeric id -> TourBox locale string key (builtinTextId).
# Built-ins are referenced in configBytes by their 16-bit id (payload[1]=0x04,
# id at payload[2:4]). The text id (e.g. "id1601") is a stable handle; the
# human label requires TourBox Console's locale table (▶ TBD). Harvested from
# the <menus> of shipped presets; extend as more are observed.
# ---------------------------------------------------------------------------
BUILTINS: dict[int, str] = {
    21: "id1601",  # Switch Presets (confirmed via calibration tourmenu)
    51: "id951", 52: "id952", 53: "id953", 54: "id954", 55: "id955",
    56: "id956", 57: "id957", 58: "id958", 59: "id959", 60: "id960",
    61: "id961", 62: "id962", 63: "id963",
}
