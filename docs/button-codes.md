# Button-code map (Elite)

Maps `configBytes` record index → physical Elite button. Confirmed by the
calibration pass (rounds 1–3); see `src/tourbox_preset/codes.py::ELITE_BUTTONS`.

| Code | Button | JSON name | Source |
|------|--------|-----------|--------|
| 0x00 | Tall            | `tall`         | 01_simple (C), x-confirmed |
| 0x01 | Side            | `side`         | 01_simple (A) |
| 0x02 | Top             | `top`          | 01_simple (B) |
| 0x03 | Short           | `short`        | 01_simple (D) |
| 0x04 | Knob — turn     | `knob`         | 02_rotary (M/N) |
| 0x09 | Scroll — turn   | `scroll`       | 02_rotary (P/Q) |
| 0x0A | Scroll — press  | `scroll_press` | 02_rotary (O) |
| 0x0F | Dial — turn     | `dial`         | 02_rotary (S/T) |
| 0x10 | Up (D-pad)      | `up`           | 01_simple (E) |
| 0x11 | Down (D-pad)    | `down`         | 01_simple (F) |
| 0x12 | Left (D-pad)    | `left`         | 01_simple (G) |
| 0x13 | Right (D-pad)   | `right`        | 01_simple (H) |
| 0x22 | C1              | `c1`           | 04_mouse (wheel up) |
| 0x23 | C2              | `c2`           | 04_mouse (wheel down) |
| 0x2A | Tour            | `tour`         | 01_simple (K) — confirm |
| 0x37 | Knob — press    | `knob_press`   | 02_rotary (L) |
| 0x38 | Dial — press    | `dial_press`   | 02_rotary (R) |

Rotary "turn" codes (0x04/0x09/0x0F) are two-direction records (type 0x08):
direction 1 at payload byte 6, direction 2 at byte 11.

## Still to map (combos)

Combinations (Side/Top/Tall/Short held with another button, e.g. `tall+knob`)
and double-clicks occupy other codes. The unmapped populated codes seen in
shipped presets (e.g. 0x05–0x0E, 0x3B, 0xCA–0xCD) are likely these — a follow-up
calibration round (assign one combo at a time) will label them. Until then they
appear in JSON as `0xNN`.
