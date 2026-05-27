"""TourBox `.tb` container layer: gzip + XStream XML + base64 <configBytes>.

This layer is fully reverse-engineered and lossless. A `.tb` file is::

    gzip( XStream-XML( <TableTransfer> ... <configBytes>BASE64</configBytes> ... ) )

The functions here read/write the gzip+XML envelope and get/set the raw
decoded ``configBytes`` blob, while preserving every other part of the XML
(``<macros>``, ``<hudList>``, ``<shortCuts>``, header bytes, etc.) byte for byte.
"""
from __future__ import annotations

import base64
import gzip
import re
from pathlib import Path
from xml.sax.saxutils import escape, unescape

__all__ = [
    "read_tb",
    "write_tb",
    "get_config_bytes",
    "set_config_bytes",
    "get_version",
    "get_short_descs",
    "get_preset_name",
    "set_preset_name",
]

# <configBytes>...</configBytes> with the base64 payload captured in group 1.
_CONFIG_RE = re.compile(r"(<configBytes>)(.*?)(</configBytes>)", re.S)
_VERSION_RE = re.compile(r"<version>(.*?)</version>", re.S)
_PRESETNAME_RE = re.compile(r"<presetName>(.*?)</presetName>", re.S)
_SHORTCUTS_RE = re.compile(r"</shortCuts>|<shortCuts/>")
_SHORTDESC_RE = re.compile(
    r"<ShortDesc>\s*<m>(\d+)</m>\s*<s>(\d+)</s>\s*<d>(.*?)</d>\s*</ShortDesc>", re.S
)


def read_tb(path: str | Path) -> str:
    """Decompress a ``.tb``/``.tbg`` file and return the inner XML string."""
    data = Path(path).read_bytes()
    return gzip.decompress(data).decode("utf-8")


def write_tb(path: str | Path, xml: str) -> None:
    """Gzip-compress ``xml`` and write it to ``path`` as a ``.tb`` file.

    Note: gzip bytes are not guaranteed to be identical to a TourBox Console
    export (compression settings differ), but the *decompressed* XML is what
    the app reads, so the result imports correctly.
    """
    raw = gzip.compress(xml.encode("utf-8"))
    Path(path).write_bytes(raw)


def get_config_bytes(xml: str) -> bytes:
    """Return the decoded binary ``configBytes`` table from the XML."""
    m = _CONFIG_RE.search(xml)
    if not m:
        raise ValueError("no <configBytes> element found")
    return base64.b64decode(m.group(2))


def set_config_bytes(xml: str, raw: bytes) -> str:
    """Return a copy of ``xml`` with ``configBytes`` replaced by ``raw``.

    Everything else in the XML is preserved exactly.
    """
    if not _CONFIG_RE.search(xml):
        raise ValueError("no <configBytes> element found")
    b64 = base64.b64encode(raw).decode("ascii")
    return _CONFIG_RE.sub(lambda m: m.group(1) + b64 + m.group(3), xml, count=1)


def get_version(xml: str) -> str | None:
    """Return the ``<version>`` text (e.g. ``"1.8"``) if present."""
    m = _VERSION_RE.search(xml)
    return m.group(1).strip() if m else None


def get_preset_name(xml: str) -> str | None:
    """Return the ``<presetName>`` text (the name shown in TourBox Console)."""
    m = _PRESETNAME_RE.search(xml)
    return unescape(m.group(1)) if m else None


def set_preset_name(xml: str, name: str) -> str:
    """Return ``xml`` with ``<presetName>`` set to ``name`` (inserted if absent)."""
    tag = f"<presetName>{escape(name)}</presetName>"
    if _PRESETNAME_RE.search(xml):
        return _PRESETNAME_RE.sub(lambda _m: tag, xml, count=1)
    # Insert right after the <shortCuts> element if there is no existing name.
    if _SHORTCUTS_RE.search(xml):
        return _SHORTCUTS_RE.sub(lambda m: m.group(0) + "\n  " + tag, xml, count=1)
    raise ValueError("cannot place <presetName>: no <presetName> or <shortCuts>")


def get_short_descs(xml: str) -> dict[int, str]:
    """Return ``{button_code: label}`` parsed from ``<ShortDesc>`` entries.

    The ``<s>`` value is the button code; ``<d>`` is the user-facing label.
    A label may reference a button whose keystroke record is empty (the button
    is bound to a macro / built-in / TourMenu).
    """
    return {
        int(s): d.strip() for _m, s, d in _SHORTDESC_RE.findall(xml)
    }
