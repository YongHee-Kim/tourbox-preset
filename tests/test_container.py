import gzip
from pathlib import Path

import pytest

from tourbox_preset import container

DATA = Path(__file__).parent / "data"
FIXTURES = sorted(DATA.glob("*.tb"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_read_and_config_bytes(path):
    xml = container.read_tb(path)
    assert "<TableTransfer>" in xml
    raw = container.get_config_bytes(xml)
    assert len(raw) == 3350


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_set_config_bytes_preserves_envelope(path):
    xml = container.read_tb(path)
    raw = container.get_config_bytes(xml)
    # Round-trip the configBytes through set/get: identical, envelope untouched.
    xml2 = container.set_config_bytes(xml, raw)
    assert container.get_config_bytes(xml2) == raw
    assert xml2 == xml  # base64 of same bytes is identical -> whole XML identical


def test_write_tb_roundtrip(tmp_path):
    xml = container.read_tb(FIXTURES[0])
    out = tmp_path / "out.tb"
    container.write_tb(out, xml)
    assert gzip.decompress(out.read_bytes()).decode("utf-8") == xml
