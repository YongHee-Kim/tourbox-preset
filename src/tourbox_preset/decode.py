""".tb file -> tourbox-preset JSON document (lossless for the binding table)."""
from __future__ import annotations

from pathlib import Path

from . import actions, codes, container
from .schema import FORMAT, SCHEMA_VERSION
from .table import ConfigTable

__all__ = ["decode_xml", "decode_file"]


def decode_xml(xml: str) -> dict:
    """Build a JSON-ready preset dict from decompressed ``.tb`` XML.

    Bindings come from the 256-record table (keyed by button code). The
    ``<ShortDesc>`` labels use a separate, not-yet-decoded key space, so they
    are surfaced under an informational ``shortcutLabels`` map rather than being
    matched to bindings (see docs/calibration.md). They are *not* re-encoded;
    on ``pack`` the labels are inherited from the base envelope.
    """
    table = ConfigTable.from_bytes(container.get_config_bytes(xml))

    bindings: dict[str, dict] = {}
    for code, payload in table.assigned().items():
        bindings[codes.button_name(code)] = actions.decode_action(payload)

    doc: dict = {"format": FORMAT, "schemaVersion": SCHEMA_VERSION}
    version = container.get_version(xml)
    if version:
        doc["tbVersion"] = version
    doc["device"] = "elite"
    name = container.get_preset_name(xml)
    if name:
        doc["name"] = name
    doc["bindings"] = bindings

    labels = container.get_short_descs(xml)
    if labels:
        # informational only (keys are raw <s> values, pending calibration)
        doc["shortcutLabels"] = {str(s): t for s, t in sorted(labels.items())}
    return doc


def decode_file(path: str | Path) -> dict:
    """Decode a ``.tb`` file path to a preset dict."""
    return decode_xml(container.read_tb(path))
