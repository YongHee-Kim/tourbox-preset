"""Unit tests for the semantic action codec + the calibration ground truth."""
import pytest

from tourbox_preset import actions, decode

# --- payload-level codec round-trips ---------------------------------------

CASES = [
    {"type": "none"},
    {"type": "key", "key": "A"},
    {"type": "key", "key": "A", "mods": ["ctrl"]},
    {"type": "key", "key": "A", "mods": ["ctrl", "shift"]},
    {"type": "key", "key": "Space"},
    {"type": "key", "key": "F1"},
    {"type": "key", "key": "ArrowUp"},
    {"type": "mouse", "action": "left"},
    {"type": "mouse", "action": "wheel_up"},
    {"type": "rotary", "cw": {"key": "]"}, "ccw": {"key": "["}},
    {"type": "rotary", "cw": {"key": "+", "mods": ["ctrl"]},
                       "ccw": {"key": "-", "mods": ["ctrl"]}},
    {"type": "raw", "hex": "08 04 01 f2 00 78 35 00 00 00 00 00"},
]


@pytest.mark.parametrize("action", CASES, ids=lambda a: a["type"] + "-" + str(a.get("key") or a.get("action") or a.get("cw", "")))
def test_action_roundtrip(action):
    payload = actions.encode_action(action)
    assert len(payload) == 12
    assert actions.decode_action(payload) == action


# --- ground truth from the calibration exports -----------------------------

def _bindings(name):
    return decode.decode_file(f"tests/data/{name}").get("bindings", {})


def test_simple_button_keys():
    b = _bindings("01_simple.tb")
    assert b["tall"] == {"type": "key", "key": "C"}
    assert b["side"] == {"type": "key", "key": "A"}
    assert b["top"] == {"type": "key", "key": "B"}
    assert b["short"] == {"type": "key", "key": "D"}
    assert b["up"] == {"type": "key", "key": "E"}
    assert b["right"] == {"type": "key", "key": "H"}


def test_modifiers():
    b = _bindings("03_modifiers.tb")
    assert b["side"] == {"type": "key", "key": "A", "mods": ["ctrl"]}
    assert b["top"] == {"type": "key", "key": "A", "mods": ["shift"]}
    assert b["tall"] == {"type": "key", "key": "A", "mods": ["alt"]}
    assert b["short"] == {"type": "key", "key": "A", "mods": ["win"]}
    assert b["up"] == {"type": "key", "key": "A", "mods": ["ctrl", "shift"]}


def test_mouse():
    b = _bindings("04_mouse.tb")
    assert b["side"] == {"type": "mouse", "action": "left"}
    assert b["top"] == {"type": "mouse", "action": "right"}
    assert b["tall"] == {"type": "mouse", "action": "middle"}
    assert b["short"] == {"type": "mouse", "action": "double"}
    assert b["c1"] == {"type": "mouse", "action": "wheel_up"}
    assert b["c2"] == {"type": "mouse", "action": "wheel_down"}


def test_rotary_turns():
    b = _bindings("02_rotary.tb")
    assert b["knob"] == {"type": "rotary", "cw": {"key": "M"}, "ccw": {"key": "N"}}
    assert b["scroll"] == {"type": "rotary", "cw": {"key": "P"}, "ccw": {"key": "Q"}}
    assert b["knob_press"] == {"type": "key", "key": "L"}


def test_special_keys():
    b = _bindings("05_specialkeys.tb")
    assert b["tall"] == {"type": "key", "key": "Tab"}
    assert b["top"] == {"type": "key", "key": "Enter"}
    assert b["short"] == {"type": "key", "key": "Esc"}
    assert b["up"] == {"type": "key", "key": "ArrowUp"}
    assert b["right"] == {"type": "key", "key": "Backspace"}
