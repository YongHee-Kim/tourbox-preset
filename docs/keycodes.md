# Key codes & modifiers

The keystroke byte lives at payload offset 6 (and offset 11 for the second
direction of a rotary). See `src/tourbox_preset/codes.py` for the live tables.

## Confirmed key codes

| Bytes | Keys | Notes |
|-------|------|-------|
| `0x41–0x5A` | `A`–`Z` | == Windows VK == ASCII upper-case |
| `0x30–0x39` | `0`–`9` | digits |
| `0x20` | `Space` | |
| `0x5B 0x5D` | `[` `]` | brush size in shipped presets |
| `0x2B 0x2D` | `+` `-` | zoom in/out (with Ctrl) |
| others (`,./;'`\` `=`) | literal | ASCII punctuation |

Any byte **not** in `KEYCODES` decodes to `raw` rather than being guessed.

Named control keys (category 0): `Tab`=0x09, `Enter`=0x0D, `Esc`=0x1B,
`Backspace`=0x08, `Delete`=0x7F, `Space`=0x20.

## Modifiers — ✅ confirmed (calibration round 2)

Bitmask at **payload byte 2**. Verified including combinations
(Ctrl+Shift=0x0A, Ctrl+Alt=0x0C).

| Modifier | Bit |
|----------|-----|
| win   | `0x01` |
| shift | `0x02` |
| alt   | `0x04` |
| ctrl  | `0x08` |

## Category byte (payload byte 3)

| Value | Meaning |
|-------|---------|
| `0x00` | normal key (code = VK/ASCII at byte 6) |
| `0x01` | extended key (arrows, F-keys) |
| `0x02` | mouse action (code at byte 6: left=1, right=2, middle=3, wheel_up=4, wheel_down=5, double=6) |

## Extended keys (category 1) — partially confirmed

| Key | Code | Confirmed? |
|-----|------|-----------|
| ArrowUp | `0x01` | ✅ |
| ArrowDown | `0x02` | ✅ |
| F1 | `0x0A` | ✅ |
| ArrowLeft / ArrowRight | ▶ TBD | next round |
| F2–F12 | ▶ TBD | next round |

Unconfirmed extended keys decode as `raw` until calibrated.
