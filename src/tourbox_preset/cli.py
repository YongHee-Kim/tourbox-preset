"""Command-line interface: ``tbtool unpack|pack|validate``."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import container, decode, encode, schema


def _cmd_unpack(args: argparse.Namespace) -> int:
    doc = decode.decode_file(args.input)
    out = args.output or Path(args.input).with_suffix(".json")
    Path(out).write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"unpacked {args.input} -> {out} ({len(doc['bindings'])} bindings)")
    return 0


def _cmd_pack(args: argparse.Namespace) -> int:
    doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    base_xml = container.read_tb(args.base) if args.base else None
    out = args.output or Path(args.input).with_suffix(".tb")
    try:
        encode.encode_to_file(doc, out, base_xml=base_xml)
    except schema.SchemaError as e:
        print(f"error: invalid preset: {e}", file=sys.stderr)
        return 2
    print(f"packed {args.input} -> {out}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        schema.validate(doc)
    except schema.SchemaError as e:
        print(f"invalid: {e}", file=sys.stderr)
        return 2
    print(f"valid: {args.input} ({len(doc['bindings'])} bindings)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tbtool", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    up = sub.add_parser("unpack", help="decode a .tb file to JSON")
    up.add_argument("input", help="path to .tb file")
    up.add_argument("-o", "--output", help="output .json (default: alongside input)")
    up.set_defaults(func=_cmd_unpack)

    pk = sub.add_parser("pack", help="encode a JSON preset to .tb")
    pk.add_argument("input", help="path to .json preset")
    pk.add_argument("-o", "--output", help="output .tb (default: alongside input)")
    pk.add_argument("--base", help="base .tb whose envelope (macros/HUD) to inherit")
    pk.set_defaults(func=_cmd_pack)

    va = sub.add_parser("validate", help="validate a JSON preset")
    va.add_argument("input", help="path to .json preset")
    va.set_defaults(func=_cmd_validate)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
