"""tourbox_preset - encode/decode TourBox Elite .tb presets to/from JSON.

Public API::

    import tourbox_preset
    doc = tourbox_preset.decode_file("Photoshop.tb")    # .tb  -> preset dict
    tourbox_preset.encode_to_file(doc, "out.tb")        # dict -> .tb
"""
from __future__ import annotations

from .decode import decode_file, decode_xml
from .encode import encode_to_file, encode_to_xml, default_template_xml
from .schema import validate, SchemaError

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "decode_file",
    "decode_xml",
    "encode_to_file",
    "encode_to_xml",
    "default_template_xml",
    "validate",
    "SchemaError",
]
