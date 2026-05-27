"""Encode/decode the 12-byte action payload <-> a JSON-friendly action dict.

Safety model
------------
Decoding is *lossless by construction*: :func:`decode_action` emits a semantic
form only when re-encoding it reproduces the original payload byte-for-byte;
otherwise it returns ``{"type": "raw", "hex": ...}``. So semantic coverage can
grow as calibration confirms more bytes, without ever risking a bad round-trip.

Payload layout (confirmed by calibration)::

    [0] type           : 0x00 single action, 0x08 two-way (rotary turn)
    [1] aux            : 0 for forms we decode (nonzero, e.g. drag, -> raw)
    [2..6]  sub-action A: [mod, category, 0, 0, keycode]
    [7..11] sub-action B: [mod, category, 0, 0, keycode]   (rotary direction 2)

Decoded today: ``none``, ``key`` (with modifiers, normal & confirmed extended
keys), ``mouse`` (click/double/wheel), ``rotary`` (two directions, each a key or
mouse action), and ``raw`` (the universal fallback). Mouse *drag* stays raw.
"""
from __future__ import annotations

from . import codes
from .table import PAYLOAD_LEN

__all__ = ["encode_action", "decode_action", "EncodeError"]

TYPE_SINGLE = 0x00
TYPE_DUAL = 0x08

# sub-action A occupies payload[2:7], sub-action B payload[7:12]
_SUBA = slice(2, 7)
_SUBB = slice(7, 12)

# reference actions (payload[0]==0, payload[1]==0): payload[2] selects the kind,
# payload[4] holds the referenced id.
AUX_BUILTIN = 0x04   # payload[1]; 16-bit big-endian id at payload[2:4]
REF_MACRO = 0x80     # payload[2]
REF_TOURMENU = 0x20  # payload[2]


class EncodeError(ValueError):
    """Raised when an action dict cannot be encoded; callers may keep raw."""


# --- sub-action (5 bytes: [mod, category, 0, 0, keycode]) ------------------

def _encode_sub(d: dict) -> bytes:
    mod = codes.mods_to_bits(d.get("mods", []))
    if "mouse" in d:
        code = codes.MOUSE.get(d["mouse"])
        if code is None:
            raise EncodeError(f"unknown mouse action {d['mouse']!r}")
        cat = codes.CAT_MOUSE
    elif "key" in d:
        try:
            cat, code = codes.resolve_key(d["key"])
        except KeyError as e:
            raise EncodeError(str(e)) from e
    else:
        raise EncodeError(f"direction must have 'key' or 'mouse': {d!r}")
    return bytes([mod, cat, 0, 0, code])


def _decode_sub(b: bytes) -> dict | None:
    if not any(b):
        return None
    mod, cat, x1, x2, code = b
    if x1 or x2:
        return None
    try:
        mods = codes.bits_to_mods(mod)
    except ValueError:
        return None
    if cat in (codes.CAT_KEY, codes.CAT_EXT):
        name = codes.key_label(cat, code)
        if name is None:
            return None
        d: dict = {"key": name}
    elif cat == codes.CAT_MOUSE:
        name = codes.mouse_name(code)
        if name is None:
            return None
        d = {"mouse": name}
    else:
        return None
    if mods:
        d["mods"] = mods
    return d


# --- encode ----------------------------------------------------------------

def encode_action(action: dict) -> bytes:
    t = action.get("type", "none")
    if t == "none":
        return bytes(PAYLOAD_LEN)
    if t == "raw":
        raw = bytes.fromhex(action["hex"].replace(" ", ""))
        if len(raw) != PAYLOAD_LEN:
            raise EncodeError(f"raw hex must be {PAYLOAD_LEN} bytes, got {len(raw)}")
        return raw

    p = bytearray(PAYLOAD_LEN)
    if t == "key":
        p[0] = TYPE_SINGLE
        p[_SUBA] = _encode_sub({"key": action["key"], "mods": action.get("mods", [])})
        return bytes(p)
    if t == "mouse":
        p[0] = TYPE_SINGLE
        p[_SUBA] = _encode_sub({"mouse": action["action"], "mods": action.get("mods", [])})
        return bytes(p)
    if t == "rotary":
        a = action.get("cw") or action.get("up")
        b = action.get("ccw") or action.get("down")
        if not (a and b):
            raise EncodeError("rotary needs two directions (cw/ccw or up/down)")
        p[0] = TYPE_DUAL
        p[_SUBA] = _encode_sub(a)
        p[_SUBB] = _encode_sub(b)
        return bytes(p)
    if t == "builtin":
        bid = int(action["id"])
        if not 0 <= bid <= 0xFFFF:
            raise EncodeError("builtin id out of range")
        p[1] = AUX_BUILTIN
        p[2:4] = bid.to_bytes(2, "big")
        return bytes(p)
    if t == "macro":
        p[2] = REF_MACRO
        p[4] = int(action["id"])
        return bytes(p)
    if t == "tourmenu":
        p[2] = REF_TOURMENU
        p[4] = int(action["id"])
        return bytes(p)
    raise EncodeError(f"action type {t!r} is not yet encodable; use raw")


# --- decode ----------------------------------------------------------------

def _single_to_action(sub: dict) -> dict:
    if "mouse" in sub:
        out = {"type": "mouse", "action": sub["mouse"]}
    else:
        out = {"type": "key", "key": sub["key"]}
    if "mods" in sub:
        out["mods"] = sub["mods"]
    return out


def _try_semantic(payload: bytes) -> dict | None:
    if not any(payload):
        return {"type": "none"}

    # built-in: payload[1]==0x04, single (payload[0]==0), 16-bit id at [2:4].
    if payload[0] == TYPE_SINGLE and payload[1] == AUX_BUILTIN and not any(payload[4:]):
        bid = int.from_bytes(payload[2:4], "big")
        out = {"type": "builtin", "id": bid}
        text = codes.BUILTINS.get(bid)
        if text:
            out["textId"] = text
        return out

    if payload[1] != 0:
        return None  # aux byte set (e.g. drag) -> raw
    b_type = payload[0]

    # macro / tourmenu references: payload[2] selects kind, id at payload[4].
    if b_type == TYPE_SINGLE and payload[2] in (REF_MACRO, REF_TOURMENU):
        others = [i for i, v in enumerate(payload) if v and i not in (2, 4)]
        if not others:
            kind = "macro" if payload[2] == REF_MACRO else "tourmenu"
            return {"type": kind, "id": payload[4]}
    sub_a = _decode_sub(payload[_SUBA])
    sub_b = _decode_sub(payload[_SUBB])

    if b_type == TYPE_SINGLE and sub_a is not None and sub_b is None:
        return _single_to_action(sub_a)
    if b_type == TYPE_DUAL and sub_a is not None and sub_b is not None:
        return {"type": "rotary", "cw": sub_a, "ccw": sub_b}
    return None


def decode_action(payload: bytes) -> dict:
    if len(payload) != PAYLOAD_LEN:
        raise ValueError(f"payload must be {PAYLOAD_LEN} bytes, got {len(payload)}")
    semantic = _try_semantic(payload)
    if semantic is not None:
        try:
            if encode_action(semantic) == payload:
                return semantic
        except EncodeError:
            pass
    return {"type": "raw", "hex": payload.hex(" ")}
