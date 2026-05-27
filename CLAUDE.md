# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A pure-Python (3.9+, no runtime deps) encoder/decoder that converts **TourBox
Elite `.tb` preset files** to/from human-readable JSON. The import package is
`tourbox_preset` (under `src/`); the distribution is `tourbox-preset`; it installs
a CLI command named **`tbtool`** (the script name is kept short — don't rename it
to match the package).

The defining constraint: this is **clean-room reverse engineering** of a
proprietary binary format. The container is fully solved and the per-button action
encoding is largely decoded; remaining unknowns are completed incrementally via a
calibration workflow. The whole design exists to make that incremental decoding
*safe* — see "Lossless-by-construction" below.

## Commands

```bash
pip install -e ".[dev]"              # install (editable) with pytest
                                     # re-run after renaming/moving the package

python -m pytest -q                  # full suite
python -m pytest tests/test_roundtrip.py   # the key safety net (run after any encode/decode change)
python -m pytest tests/test_roundtrip.py -k Photoshop   # single fixture by name

tbtool unpack "samples/Photoshop.tb" -o out.json   # .tb -> JSON
tbtool pack out.json -o out.tb                     # JSON -> .tb (uses bundled blank template)
tbtool pack out.json -o out.tb --base "samples/Photoshop.tb"   # inherit macros/HUD/menus from a real preset
tbtool validate out.json

python tools/analyze.py diff base.tb variant.tb   # calibration: show which records changed
python tools/unpack.py                            # dump all *.tb/*.tbg in cwd into ./dec for inspection
```

Note `tbtool unpack` (the CLI subcommand) and `tools/unpack.py` (a standalone
inspection dumper, no package dependency) are different things despite the name.

## Architecture — three stacked layers

A `.tb` file is `gzip( XStream-XML( ... <configBytes>BASE64</configBytes> ... ) )`
where `configBytes` decodes to a fixed **3350-byte binary table**:

```
.tb  ──gunzip──►  XStream XML  ──base64──►  configBytes (3350 B)
                                            = 22-byte header + 256 × 13-byte records
```

The code mirrors this onion exactly; each layer only touches its own concern:

1. **`container.py`** — gzip + XML envelope. Reads/writes the `.tb`, and
   gets/sets the decoded `configBytes` blob (and the preset `<name>` / `<version>`)
   via *regex substitution* on the XML string. Everything else (`<macros>`,
   `<hudList>`, `<menus>`, header bytes, `<ShortDesc>` labels) is preserved
   verbatim — the encoder never reconstructs the envelope, it splices into a base.

2. **`table.py`** — `ConfigTable`: 22-byte opaque header + 256 fixed 13-byte
   records. `record[0]` is a self-referential index (`== code`), bytes 1–12 are
   the action payload. All-zero payload = unassigned. The header is opaque and
   copied from the base envelope.

3. **`actions.py`** — the 12-byte action payload ⇄ a JSON action dict. This is the
   reverse-engineering frontier.

`decode.py` / `encode.py` orchestrate the layers. **`encode.py` patches, it does
not rebuild**: it starts from the base table's payloads and overwrites only the
records named in the JSON — so a record you don't mention keeps the device's
original bytes (including the structural `08 00..` two-way placeholders). Use
`{"type": "none"}` to explicitly clear a button. `__init__.py` re-exports
`decode_file` / `encode_to_file` / `validate`; `schema.py` is a dependency-free
validator; `cli.py` wires up `unpack/pack/validate`; `codes.py` holds the lookup
tables (kept intentionally sparse — see below).

### Action payload layout (12 bytes, confirmed by calibration)

```
[0] type    : 0x00 single action · 0x08 two-way (rotary turn)
[1] aux     : 0 for the forms we decode; 0x04 = built-in ref (16-bit id at [2:4]);
              other nonzero (e.g. mouse drag) -> raw
[2:7]  sub-action A : [mod, category, 0, 0, keycode]
[7:12] sub-action B : [mod, category, 0, 0, keycode]   (rotary 2nd direction)

mod bits : Win=0x01 Shift=0x02 Alt=0x04 Ctrl=0x08   (codes.MODS)
category : 0 normal key · 1 extended key (arrows/F-keys) · 2 mouse   (codes.CAT_*)
macro / tourmenu refs : payload[2] = 0x80 (macro) / 0x20 (tourmenu), id at payload[4]
```

Decoded today: `none`, `key` (+`mods`, normal & confirmed extended keys), `mouse`
(click/double/wheel), `rotary` (two directions, each a key or mouse action),
`builtin`/`macro`/`tourmenu` (by id), and `raw`.

## Lossless-by-construction — the central invariant

The most important thing to understand before touching `actions.py` or `codes.py`:

`actions.decode_action()` emits a semantic form **only when re-encoding it
reproduces the original payload byte-for-byte** (`encode_action(semantic) ==
payload`, checked inside `decode_action`). Otherwise it returns
`{"type": "raw", "hex": "..."}`.

Consequences you must respect:
- **You cannot break round-trip fidelity by adding a mapping.** Worst case, a
  payload you mapped wrong simply stays `raw`. This is *why* `codes.py` is
  intentionally sparse — an unconfirmed byte returns `None`/raises so decoding
  falls back to raw rather than guessing.
- The encoder only ever changes `configBytes` (and the preset name); the rest of
  the XML envelope is inherited from a base (`templates/elite_base.xml`, or a user
  `--base`).
- `<ShortDesc>` labels use a separate, not-yet-decoded key space (the `<s>` values
  exceed 255), so they are surfaced informationally as `shortcutLabels` and are
  *not* re-encoded — they ride along from the base envelope.

`tests/test_roundtrip.py` enforces this for every `.tb` in `tests/data/`:
decode→encode must reproduce the binding table exactly. **Always run it after any
change to encode/decode/codes.**

## Tests

- `tests/test_container.py`, `tests/test_table.py`, `tests/test_roundtrip.py` —
  the container/table/round-trip safety nets, parametrized over `tests/data/*.tb`.
- `tests/test_actions.py` — the **calibration ground truth**: it decodes the
  calibration sample exports (`tests/data/01_simple.tb`, `02_rotary.tb`,
  `03_modifiers.tb`, `04_mouse.tb`, `05_specialkeys.tb`) and asserts the exact
  decoded bindings (button names, mods, mouse, special keys). When you confirm a
  new mapping, add/extend a case here.
- `tests/data/` therefore holds both real shipped presets *and* the calibration
  exports; `test_actions.py` reads the latter by name, so don't move them.

## Extending the decode (calibration workflow)

Decode more of the format by **known-plaintext diffing**, not guessing: make one
controlled change in TourBox Console, export, and
`python tools/analyze.py diff base.tb variant.tb` to see exactly which
record/bytes moved. The `samples/` directory is the working area for these
exports — `samples/CALIBRATION_SAMPLES.md` lists the exact presets/filenames to
create, round by round. Then:

1. Add the confirmed mapping to `src/tourbox_preset/codes.py` and/or the decode
   logic in `actions.py`, plus a matching encoder branch.
2. Confirm `pytest` still passes (round-trip proves you can't regress fidelity;
   add a `test_actions.py` assertion for the new form).
3. Update `docs/format.md`, `docs/button-codes.md`, `docs/keycodes.md`, and flip
   the matching ▶TBD → ✅ cell in the README coverage matrix.

Full method and recommended change sequence: `docs/calibration.md`. Reverse-
engineered format spec: `docs/format.md`.

## Known boundaries (currently `raw` / TBD)

Mouse **drag** (type `0x08` with extra aux bytes), extended keys beyond Arrow
Up/Down + F1, **mode flags** (UP/REP/Speed/Haptic), built-in *human labels* (the
numeric id/`textId` is decoded, but the label needs TourBox Console's locale
table), and **button combos** (`tall+knob`, …, still keyed by `0xNN`) are not yet
decoded — all round-trip as `raw`. `.tbg` group files (multiple configs under
`<subTableTransfers>`) are a later milestone; current scope is single `.tb` files.

## Project layout

```
src/tourbox_preset/   container.py · table.py · actions.py · codes.py
                      schema.py · decode.py · encode.py · cli.py · templates/
tools/                unpack.py (inspection dumper) · analyze.py (calibration diff)
tests/                container / table / round-trip / actions tests + data/ fixtures
docs/                 format.md · button-codes.md · keycodes.md · calibration.md
samples/              shipped TourBox presets + calibration exports (00_*..09_*)
                      + CALIBRATION_SAMPLES.md; repacked/ holds pack outputs
presets/              example hand-written JSON preset(s)
```

`tests/data/` is self-contained (its own fixture copies), so the round-trip and
action tests don't depend on `samples/`.
