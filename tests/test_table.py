from pathlib import Path

import pytest

from tourbox_preset import container
from tourbox_preset.table import ConfigTable, TABLE_LEN, PAYLOAD_LEN

DATA = Path(__file__).parent / "data"
FIXTURES = sorted(DATA.glob("*.tb"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_table_roundtrip_bytes(path):
    raw = container.get_config_bytes(container.read_tb(path))
    table = ConfigTable.from_bytes(raw)
    assert table.to_bytes() == raw
    assert len(table.to_bytes()) == TABLE_LEN


def test_empty_table_invariants():
    t = ConfigTable.empty()
    raw = t.to_bytes()
    assert len(raw) == TABLE_LEN
    # record[0] == index for all 256 records
    body = raw[22:]
    for i in range(256):
        assert body[i * 13] == i
    assert t.assigned() == {}


def test_setitem_getitem():
    t = ConfigTable.empty()
    t[0x10] = bytes([0, 0, 0, 0, 0, 0, 0x45, 0, 0, 0, 0, 0])
    assert t[0x10][6] == 0x45
    assert set(t.assigned()) == {0x10}
    with pytest.raises(ValueError):
        t[0x10] = b"\x00" * (PAYLOAD_LEN - 1)
