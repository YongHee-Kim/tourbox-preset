# Calibration workflow

The container and table layout are fully solved. The remaining unknowns — the
exact keycode/modifier bytes, mouse/wheel/mode encodings, the button-code →
button-name map, and the `<ShortDesc><s>` key space — are completed by
**known-plaintext diffing**: make one controlled change in TourBox Console,
export, and diff against a baseline.

## Setup

1. In TourBox Console, create a preset and export it as the **baseline** (`base.tb`).
2. Keep `base.tb` and each variant in a folder, e.g. `samples/`.

## Method (change one variable at a time)

```bash
# dump the raw 256x13 table for two exports and show only the records that differ
python tools/analyze.py diff samples/base.tb samples/variant.tb
```

Recommended sequence:

1. **Keycodes** — same button, assign single keys `A, B, 1, Space, F1, …`.
   Confirms the keycode table and that the code sits at payload byte 6.
2. **Modifiers** — add `Ctrl`, `Shift`, `Alt`, `Win` one at a time to one key.
   Locate the modifier byte and each bit value.
3. **Mouse / wheel** — assign left/right/middle click, double-click, wheel
   up/down, drag. Maps the non-zero action-type values (`0x04/05/09/0A`).
4. **Modes** — toggle UP, REP, Speed (Slow1/Slow2), Haptic (Vib1/Vib2). Find the
   mode-flag bits.
5. **Button map** — assign a unique, identifiable action to **each physical
   button and combo** once. The record index that changes = that button's code.
   Fill `ELITE_BUTTONS` in `src/tourbox_preset/codes.py`.
6. **Macros / built-ins / TourMenu** — assign each; see how the record references
   `<macros>` ids / built-in ids, and decode the `<ShortDesc><s>` numbering.

## Recording results

For each confirmed fact:
- add the mapping to `src/tourbox_preset/codes.py` (`ELITE_BUTTONS`, `MODS`,
  `BUILTINS`, the key/mouse tables) and/or the decode logic in
  `src/tourbox_preset/actions.py`;
- extend the semantic encoder so the new form round-trips (the test suite will
  prove it: `pytest tests/test_roundtrip.py`);
- update `docs/format.md`, `docs/button-codes.md`, `docs/keycodes.md`;
- flip the matching cell in the README coverage matrix from ▶TBD to ✅.

Because decoding is "semantic only if it re-encodes exactly", you can never break
round-trip fidelity by adding a mapping — worst case a payload stays `raw`.
