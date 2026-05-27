"""The ``configBytes`` binary table: a 22-byte header + 256 fixed records.

Layout (verified identical across every TourBox Elite ``.tb`` preset)::

    offset 0                     : 22-byte header (opaque, preserved verbatim)
    offset 22 + code*13          : record for button `code` (0x00..0xFF)
        record[0]                : button code == its own index (self-referential)
        record[1..12]            : 12-byte action payload (all zero == unassigned)

Total size = 22 + 256*13 = 3350 bytes.
"""
from __future__ import annotations

__all__ = ["HEADER_LEN", "RECORD_LEN", "RECORD_COUNT", "TABLE_LEN", "PAYLOAD_LEN", "ConfigTable"]

HEADER_LEN = 22
RECORD_LEN = 13
RECORD_COUNT = 256
PAYLOAD_LEN = RECORD_LEN - 1  # 12
TABLE_LEN = HEADER_LEN + RECORD_COUNT * RECORD_LEN  # 3350


class ConfigTable:
    """Mutable view over the 256-record button table.

    Index by button code to read/write the 12-byte action payload::

        t = ConfigTable.from_bytes(raw)
        payload = t[0x10]            # bytes, length 12
        t[0x10] = b"\\x00" * 12       # clear a binding
        raw = t.to_bytes()
    """

    def __init__(self, header: bytes, payloads: list[bytes]):
        if len(header) != HEADER_LEN:
            raise ValueError(f"header must be {HEADER_LEN} bytes, got {len(header)}")
        if len(payloads) != RECORD_COUNT:
            raise ValueError(f"expected {RECORD_COUNT} payloads, got {len(payloads)}")
        self.header = bytes(header)
        self.payloads = [bytes(p) for p in payloads]
        for i, p in enumerate(self.payloads):
            if len(p) != PAYLOAD_LEN:
                raise ValueError(f"payload {i:#04x} must be {PAYLOAD_LEN} bytes, got {len(p)}")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "ConfigTable":
        if len(raw) != TABLE_LEN:
            raise ValueError(f"configBytes must be {TABLE_LEN} bytes, got {len(raw)}")
        header = raw[:HEADER_LEN]
        body = raw[HEADER_LEN:]
        payloads = []
        for i in range(RECORD_COUNT):
            rec = body[i * RECORD_LEN:(i + 1) * RECORD_LEN]
            if rec[0] != i:
                raise ValueError(f"record {i:#04x} has byte0={rec[0]:#04x}, expected index")
            payloads.append(rec[1:])
        return cls(header, payloads)

    @classmethod
    def empty(cls, header: bytes | None = None) -> "ConfigTable":
        """A table with all bindings cleared (optionally a custom header)."""
        hdr = header if header is not None else bytes(HEADER_LEN)
        return cls(hdr, [bytes(PAYLOAD_LEN) for _ in range(RECORD_COUNT)])

    def to_bytes(self) -> bytes:
        out = bytearray(self.header)
        for i, p in enumerate(self.payloads):
            out.append(i)          # record[0] == index
            out.extend(p)
        assert len(out) == TABLE_LEN
        return bytes(out)

    def __getitem__(self, code: int) -> bytes:
        return self.payloads[code]

    def __setitem__(self, code: int, payload: bytes) -> None:
        if len(payload) != PAYLOAD_LEN:
            raise ValueError(f"payload must be {PAYLOAD_LEN} bytes, got {len(payload)}")
        self.payloads[code] = bytes(payload)

    def assigned(self) -> dict[int, bytes]:
        """Return ``{code: payload}`` for every non-empty (assigned) record."""
        return {i: p for i, p in enumerate(self.payloads) if any(p)}
