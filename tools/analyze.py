#!/usr/bin/env python3
"""Static-analysis helpers for calibration (known-plaintext diffing).

Usage:
    python tools/analyze.py dump  FILE.tb            # list non-empty records
    python tools/analyze.py diff  BASE.tb VARIANT.tb # show records that changed

`diff` is the workhorse: change one thing in TourBox Console, export, and see
exactly which record/bytes moved. Uses only the stdlib + the solved container.
"""
import base64
import gzip
import re
import sys
from pathlib import Path

HEADER, REC = 22, 13


def table(path):
    xml = gzip.decompress(Path(path).read_bytes()).decode("utf-8")
    raw = base64.b64decode(re.search(r"<configBytes>(.*?)</configBytes>", xml, re.S).group(1))
    body = raw[HEADER:]
    return {i: body[i * REC + 1:(i + 1) * REC] for i in range(256)}


def cmd_dump(path):
    t = table(path)
    for i, p in t.items():
        if any(p):
            print(f"{i:02X}  {p.hex(' ')}")


def cmd_diff(base, variant):
    a, b = table(base), table(variant)
    changed = [i for i in range(256) if a[i] != b[i]]
    if not changed:
        print("(no record differences)")
        return
    print(f"# {len(changed)} record(s) differ")
    print(f"# code   base                          ->  variant")
    for i in changed:
        print(f"{i:02X}     {a[i].hex(' '):<28}  ->  {b[i].hex(' ')}")


def main(argv):
    if len(argv) >= 2 and argv[0] == "dump":
        return cmd_dump(argv[1])
    if len(argv) >= 3 and argv[0] == "diff":
        return cmd_diff(argv[1], argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
