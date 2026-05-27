# tourbox-preset

Convert **TourBox Elite** `.tb` preset files to and from human-readable **JSON** —
so you can version, diff, hand-edit, and share your button mappings as plain text,
then import them straight back into TourBox Console.

> The Python package is `tourbox-preset`; it installs a CLI command named
> **`tbtool`** (short for "the `.tb` tool").

## What problem this solves

The [TourBox Elite](https://www.tourbox.design/) is a one-handed physical
controller — a dial, a scroll wheel, a knob, and a cluster of buttons — that
creatives map to keyboard shortcuts in Photoshop, Lightroom, Premiere, DaVinci
Resolve, Clip Studio Paint, and similar apps. Each app's mapping is saved by
**TourBox Console** as a `.tb` preset file.

A `.tb` file is an opaque, gzip-compressed binary blob, which makes everyday
things awkward: you can't open it in a text editor to see what a button does,
`diff` two versions, track tweaks in git, copy one binding into another preset,
or share a change as a readable patch.

`tourbox-preset` turns a `.tb` into clean JSON and back again:

```
Photoshop.tb  ──unpack──►  photoshop.json   (edit / diff / commit / share)
photoshop.json  ──pack──►  photoshop.tb     (import into TourBox Console)
```

It is built to be **trustworthy with your presets**:

- **Lossless** — decode → encode reproduces the binding table byte-for-byte for
  every shipped preset (enforced by the test suite).
- **Safe by design** — anything not yet fully understood survives as `raw` hex,
  so nothing is ever guessed or silently dropped.
- **Self-contained** — pure Python (3.9+), no runtime dependencies, MIT-licensed.

> Only the **Elite** device is supported today. This project is not affiliated
> with or endorsed by TourBox; `.tb` is TourBox's proprietary format, and this is
> clean-room reverse engineering for interoperability.

## Coverage matrix

| Area | Status |
|------|--------|
| gzip + XML + base64 container | ✅ solved |
| 256×13 binding table (header + records) | ✅ solved |
| Lossless round-trip (decode↔encode) | ✅ verified in tests |
| Single key (`A–Z`, `0–9`, Space, named control keys) | ✅ |
| Modifier keys (Ctrl/Shift/Alt/Win, incl. combos) | ✅ |
| Two-way rotary (keys or mouse, per direction) | ✅ |
| Mouse click / double / wheel | ✅ |
| Button-code → name map (Elite core buttons + rotary) | ✅ |
| Extended keys (arrows / F-keys) | ◑ partial (Up/Down/F1) |
| Mouse drag | ▶ TBD (raw) |
| Mode flags (UP / REP / Speed / Haptic) | ▶ TBD (raw) |
| Macro / built-in / TourMenu refs | ▶ TBD (raw) |
| Button combos (`tall+knob`, …) | ▶ TBD (keyed by `0xNN`) |
| `<ShortDesc>` label key space | ▶ TBD (informational) |
| `.tbg` group files | ▶ later milestone |

Anything marked TBD round-trips losslessly as `raw` today; semantic coverage
grows as more of the format is calibrated.

## Install

Not yet on PyPI — install from a clone:

```bash
pip install -e .            # from the repo root (Python 3.9+)
pip install -e ".[dev]"     # + pytest for the test suite
```

## Quick start

```bash
# .tb -> JSON  (the repo ships example presets under samples/)
tbtool unpack "samples/Photoshop.tb" -o photoshop.json

# edit photoshop.json in your editor, then JSON -> .tb
tbtool pack photoshop.json -o photoshop.out.tb

# inherit macros/HUD/menus from one of your own presets instead of the blank template
tbtool pack photoshop.json -o photoshop.out.tb --base "samples/Photoshop.tb"

# validate without writing
tbtool validate photoshop.json
```

Library API:

```python
import tourbox_preset
doc = tourbox_preset.decode_file("samples/Photoshop.tb")   # -> preset dict
tourbox_preset.encode_to_file(doc, "out.tb")               # dict -> .tb
```

## JSON format

```jsonc
{
  "format": "tourbox-preset",
  "schemaVersion": 1,
  "tbVersion": "1.8",            // preserved into <version>
  "device": "elite",
  "name": "My Photoshop",        // preset name, round-tripped
  "bindings": {
    // keyed by Elite button name (or "0xNN" for a button/combo not yet named)
    "side":  { "type": "key",    "key": "E", "label": "Eraser" },
    "top":   { "type": "key",    "key": "A", "mods": ["ctrl"] },
    "knob":  { "type": "rotary", "cw": { "key": "]" }, "ccw": { "key": "[" } },
    "c1":    { "type": "mouse",  "action": "wheel_up" },
    "0x25":  { "type": "raw",    "hex": "08 04 00 13 00 00 00 00 00 00 00 00" }
  }
}
```

- **Button names**: `side`, `top`, `tall`, `short`; `up`/`down`/`left`/`right`
  (D-pad); `knob`, `scroll`, `dial` (rotaries, with `*_press` variants); `c1`,
  `c2`, `tour`. A button/combo not yet named appears as its hex code (`"0x25"`) —
  both forms are accepted on pack.
- **Action types**: `key` (`key` + optional `mods`), `rotary` (`cw`/`ccw` or
  `up`/`down`, each a key or mouse action), `mouse` (`action`), `builtin` /
  `macro` / `tourmenu` (by `id`), `none`, and `raw` (12-byte hex passthrough — the
  universal lossless fallback).
- `label` is optional metadata and does not affect the binary.
- **Omitting** a button keeps whatever the base preset had on it; use
  `{"type": "none"}` to explicitly clear a button.

See [docs/format.md](docs/format.md) for the full reverse-engineered spec.

## Internals & contributing

Architecture, the lossless-by-construction design, and the **calibration
workflow** for decoding more of the format are documented for contributors in
[CLAUDE.md](CLAUDE.md) and [docs/](docs/).

## License

MIT — see [LICENSE](LICENSE).
