#!/usr/bin/env python3
"""Unpack TourBox .tb / .tbg files into ./dec for inspection.

Standalone inspection dumper (no package dependency) used during reverse
engineering and calibration. For the library API use `tourbox_preset` instead.
Run from the repo root: `python tools/unpack.py`
"""
import base64, gzip, pathlib, re, xml.dom.minidom as minidom

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEC  = ROOT / "dec"
DEC.mkdir(exist_ok=True)

HEADER_LEN = 22
RECORD_LEN = 13

def load_xml(path: pathlib.Path) -> str:
    return gzip.decompress(path.read_bytes()).decode("utf-8")

def labels(xml: str) -> dict[int, str]:
    out = {}
    for m in re.finditer(r"<ShortDesc>\s*<m>(\d+)</m>\s*<s>(\d+)</s>\s*<d>(.*?)</d>",
                          xml, re.S):
        out[int(m.group(2))] = m.group(3).strip()
    return out

def dump_table(xml: str) -> tuple[str, bytes]:
    m = re.search(r"<configBytes>(.*?)</configBytes>", xml, re.S)
    raw = base64.b64decode(m.group(1)) if m else b""
    lab = labels(xml)
    body = raw[HEADER_LEN:]
    lines = [f"# header({HEADER_LEN}B): {raw[:HEADER_LEN].hex(' ')}",
             "# idx  b0  payload[1..12]                         label"]
    for i in range(len(body) // RECORD_LEN):
        rec = body[i*RECORD_LEN:(i+1)*RECORD_LEN]
        if any(rec[1:]):                       # skip fully-empty bindings
            lines.append(f"{i:02X}   {rec[0]:02X}  {rec[1:].hex(' '):<38} "
                         f"{lab.get(i, '')}")
    return "\n".join(lines), raw

def main() -> None:
    for path in sorted([*ROOT.glob("*.tb"), *ROOT.glob("*.tbg")]):
        xml = load_xml(path)
        stem = path.name
        (DEC / f"{stem}.xml").write_text(
            minidom.parseString(xml).toprettyxml(indent="  "), encoding="utf-8")
        table, raw = dump_table(xml)
        (DEC / f"{stem}.table.txt").write_text(table, encoding="utf-8")
        (DEC / f"{stem}.configBytes.bin").write_bytes(raw)
        print(f"unpacked {stem}  -> xml + table ({len(raw)} cfg bytes)")

if __name__ == "__main__":
    main()
