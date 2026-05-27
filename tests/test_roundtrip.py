"""The core safety net: decode -> encode must reproduce the binding table
byte-for-byte, for every shipped preset, using that preset as its own base."""
from pathlib import Path

import pytest

from tourbox_preset import container, decode, encode, actions
from tourbox_preset.table import ConfigTable

DATA = Path(__file__).parent / "data"
FIXTURES = sorted(DATA.glob("*.tb"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_config_bytes_roundtrip(path):
    xml = container.read_tb(path)
    original = container.get_config_bytes(xml)

    doc = decode.decode_xml(xml)
    # Re-encode using the same file as the base envelope so header/macros match.
    out_xml = encode.encode_to_xml(doc, base_xml=xml)
    result = container.get_config_bytes(out_xml)

    assert result == original


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_every_payload_roundtrips_through_actions(path):
    raw = container.get_config_bytes(container.read_tb(path))
    table = ConfigTable.from_bytes(raw)
    for code, payload in table.assigned().items():
        action = actions.decode_action(payload)
        assert actions.encode_action(action) == payload, f"code {code:#04x}"
