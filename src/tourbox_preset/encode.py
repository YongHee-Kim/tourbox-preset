"""tourbox-preset JSON document -> .tb file.

The encoder splices a freshly built 256-record table into a base XML envelope
(which supplies the header bytes and the ``<macros>`` / ``<hudList>`` sections).
By default a bundled blank Elite template is used; pass ``base_xml`` (e.g. the
decompressed XML of one of your own presets) to inherit its macros/HUD.
"""
from __future__ import annotations

from importlib import resources
from pathlib import Path

from . import actions, codes, container, schema
from .table import ConfigTable

__all__ = ["default_template_xml", "encode_to_xml", "encode_to_file"]


def default_template_xml() -> str:
    """Return the bundled blank Elite envelope XML."""
    return (resources.files("tourbox_preset.templates") / "elite_base.xml").read_text(
        encoding="utf-8"
    )


def encode_to_xml(doc: dict, base_xml: str | None = None) -> str:
    """Encode a validated preset ``doc`` into decompressed ``.tb`` XML."""
    schema.validate(doc)
    base = base_xml if base_xml is not None else default_template_xml()

    # Start from the base table and patch in the JSON bindings. Records not
    # named in the JSON keep the base's value, which preserves the device's
    # structural "08 00.." two-way placeholders (rotary/combo slots). To clear a
    # button explicitly, give it {"type": "none"}.
    base_table = ConfigTable.from_bytes(container.get_config_bytes(base))
    table = ConfigTable(base_table.header, list(base_table.payloads))

    for name, action in doc["bindings"].items():
        code = codes.button_code(name)
        # "label" is metadata only; it never affects the binary payload.
        payload = actions.encode_action({k: v for k, v in action.items() if k != "label"})
        table[code] = payload

    out = container.set_config_bytes(base, table.to_bytes())
    if doc.get("name"):
        out = container.set_preset_name(out, doc["name"])
    return out


def encode_to_file(doc: dict, path: str | Path, base_xml: str | None = None) -> None:
    """Encode ``doc`` and write it as a gzip-compressed ``.tb`` file."""
    container.write_tb(path, encode_to_xml(doc, base_xml))
