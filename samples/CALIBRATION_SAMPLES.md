# Calibration samples to create in TourBox Console

Create each preset below, then **export** it (preset list → hamburger menu →
Export) and save the `.tb` here in `samples/` with the **exact filename** shown.
Drop them in and I'll diff them to fill in `src/tourbox_preset/codes.py`.

## Ground rules (important)

- **Create each preset "from scratch"** (the `+` icon) so it starts blank.
- For Round 1, assign **plain single keystrokes only**: just type the key in the
  shortcut field. **No** modifiers, **no** Repeat (REP), **no** UP mode, **no**
  double-click, **no** name needed. One key per button.
- Assign **exactly** the keys listed — the specific key is how I identify which
  record belongs to which button. If a button can't take a key, skip it and tell me.
- Device: **TourBox Elite**, Windows export.

---

## Round 1 — PRIORITY (button map + keycodes). Do these first.

### `00_base.tb`
A new from-scratch preset with **nothing assigned**. Export as-is. (Baseline.)

### `01_simple.tb`
Assign these plain single keys:

| Button | Key |
|--------|-----|
| Side   | A |
| Top    | B |
| Tall   | C |
| Short  | D |
| Up (D-pad)    | E |
| Down (D-pad)  | F |
| Left (D-pad)  | G |
| Right (D-pad) | H |
| C1     | I |
| C2     | J |
| Tour   | K |

### `02_rotary.tb`
Assign plain single keys to the rotary controls (press and each turn direction):

| Control | Key |
|---------|-----|
| Knob — press        | L |
| Knob — turn left    | M |
| Knob — turn right   | N |
| Scroll — press      | O |
| Scroll — turn up    | P |
| Scroll — turn down  | Q |
| Dial — press        | R |
| Dial — turn left    | S |
| Dial — turn right   | T |

> After these three I can name every button and decode most existing presets.

---

## Round 2 — modifiers

### `03_modifiers.tb`
Same buttons as `01`, same letter `A`, but **with one modifier each**:

| Button | Shortcut |
|--------|----------|
| Side  | Ctrl + A |
| Top   | Shift + A |
| Tall  | Alt + A |
| Short | Win + A   (Cmd on macOS) |
| Up    | Ctrl + Shift + A |
| Down  | Ctrl + Alt + A |

---

## Round 3 — mouse & wheel

### `04_mouse.tb`

| Button | Action |
|--------|--------|
| Side  | Mouse Left Click |
| Top   | Mouse Right Click |
| Tall  | Mouse Middle Click |
| Short | Mouse Double Click (left) |
| C1    | Wheel Scroll Up |
| C2    | Wheel Scroll Down |
| Dial   | Mouse Drag Simulation, Left Click, Horizontal,|
| Knob  | Mouse Drag, Right Click, Vertical, Reverse, ResetToOrigin, | 

---

## Round 4 — special keys

### `05_specialkeys.tb`

| Button | Key |
|--------|-----|
| Side  | F1 |
| Top   | Enter |
| Tall  | Tab |
| Short | Esc |
| Up    | Arrow Up |
| Down  | Arrow Down |
| Left  | Delete |
| Right | Backspace |

---

## Round 5 — modes (UP / REP / Speed / Haptic)

### `06_modes.tb`
Start from the Round 1 assignments, then toggle modes (leave the keys the same):

| Button | Key | Toggle |
|--------|-----|--------|
| Side | A | **UP** on |
| Top  | B | **REP** on |
| Knob — turn (M/N) | keep | **Speed = Slow 1** |
| Scroll — turn (P/Q) | keep | **Haptic = Vib 1** |

### `06b_modes2.tb` (optional)
Same as `06` but **Speed = Slow 2** and **Haptic = Vib 2** (confirms 2-level fields).

---

## Round 6 — macro / built-in / TourMenu

### `07_builtin.tb`

| Button | Built-in feature |
|--------|------------------|
| Side | Switch Presets |
| Top  | Open/Close the D-pad HUD |
| Tall  | Open/Close the General HUD |
| Short | Open/Close Guide |

### `08_macro.tb`
On **Tall**, create a Macro named `M1` with three actions in order:
1. Keystroke `X`
2. Delay `100 ms`
3. Keystroke `Y`

On **Short**, create a Macro named `M2` with three actions in order:
1. Text:Hello World
2. Mouse Move to: (x.100, y.100) / cursorspeed_slow
3. Mouse Dragging: From(x.100, y.100)/ Delay 100 / to(x.200, y.200) / cursoespeed_fast

On **Top**, create a Macro named `M3` with three actions in order:
1. OpenFolder: "C:\"
2. OpenLink: "www.google.com"

### `09_tourmenu.tb`
On **Tall**, create a TourMenu named `T1` with two items:
1. Keystroke `Z`
2. Built-in `Switch Presets`

---

When files are in `samples/`, run (or ask me to run):

```bash
python tools/analyze.py diff samples/00_base.tb samples/01_simple.tb
```
