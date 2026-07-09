# Calibration samples to create in TourBox Console

Create each preset below, then **export** it (preset list → hamburger menu →
Export) and save the `.tb` here in `samples/` with the **exact filename** shown.
Drop them in and I'll diff them to fill in `src/tourbox_preset/codes.py`.

## Ground rules (important)

- **Create each preset "from scratch"** (the `+` icon) so it starts blank, unless
  a round says to start *from an earlier preset's assignments* (the combo round
  does — it needs a known baseline so the diff isolates one change).
- **Change one variable at a time.** The whole method is known-plaintext diffing:
  if a variant differs from its baseline in exactly one setting, the single
  record/byte that moves *is* that setting. Bundling changes makes a diff
  unreadable — that's why the old mouse-drag/mode samples couldn't be decoded.
- Assign **exactly** the keys/values listed — the specific key is how I identify
  which record belongs to which button. If a button or option can't take a value,
  skip it and tell me.
- **Use a unique key per button** within a preset wherever possible, so each
  changed record is self-identifying.
- Device: **TourBox Elite**, **Windows** export.
- **Exception — mode flags (UP / REP / Speed / Haptic):** these are *not* exposed
  for a user to toggle on a from-scratch preset; they only exist baked into
  built-in/shipped presets. So they can't be created here — they're decoded by
  analysing the presets that already ship with them. See **Round 5**.

## How these map to the README coverage matrix

| Matrix row | Status | How it's tackled |
|------------|--------|------------------|
| Single key, modifiers, rotary, mouse click/wheel, button map | ✅ done | Rounds 1–3 (`00`–`05`) |
| Macro / built-in / TourMenu refs | ✅ samples in hand | Round 6 (`07`–`09`) |
| **Extended keys (arrows / F-keys)** | ◑ partial → finish | **Round 7** (`10`, `10b`) |
| **Mouse drag** | ▶ TBD | **Round 8** (`11a`–`11f`) |
| **Mode flags (UP / REP / Speed / Haptic)** | ▶ TBD (not user-settable) | **Round 5** — *decode shipped presets, no export* |
| **Button combos (`tall+knob`, …)** | ▶ TBD | **Round 9** (`12_*`) |
| **`<ShortDesc>` label key space** | ▶ TBD | **Round 10** (`13_labels`) |
| `.tbg` group files | later | **Round 11** (no new export needed) |

Rounds 1–3 and 6 are **already in `samples/`** — their tables are reproduced
below as the ground truth the test suite (`tests/test_actions.py`) asserts
against, so **do not change those assignments**. The remaining work: Rounds 7–10
need new exports; Round 5 and Round 11 are analysis of presets we already have.

---

# Done — already in `samples/` (do not change)

## Round 1 — ✅ button map + keycodes

### `00_base.tb`
A new from-scratch preset with **nothing assigned**. Export as-is. (Baseline.)

### `01_simple.tb`
Plain single keys (no modifiers, no modes):

| Button | Key |
|--------|-----|
| Side          | A |
| Top           | B |
| Tall          | C |
| Short         | D |
| Up (D-pad)    | E |
| Down (D-pad)  | F |
| Left (D-pad)  | G |
| Right (D-pad) | H |
| C1            | I |
| C2            | J |
| Tour          | K |

### `02_rotary.tb`
Plain single keys on the rotary controls (press + each turn direction):

| Control | Key |
|---------|-----|
| Knob — press   | L |
| Knob — left    | M |
| Knob — right   | N |
| Scroll — press | O |
| Scroll — up    | P |
| Scroll — down  | Q |
| Dial — press   | R |
| Dial — left    | S |
| Dial — right   | T |

## Round 2 — ✅ modifiers

### `03_modifiers.tb`
Same buttons as `01`, key `A`, but with one modifier each:

| Button | Shortcut |
|--------|----------|
| Side  | Ctrl + A |
| Top   | Shift + A |
| Tall  | Alt + A |
| Short | Win + A (Cmd on macOS) |
| Up    | Ctrl + Shift + A |
| Down  | Ctrl + Alt + A |

## Round 3 — ✅ mouse click / double / wheel

### `04_mouse.tb`

| Button | Action |
|--------|--------|
| Side  | Mouse Left Click |
| Top   | Mouse Right Click |
| Tall  | Mouse Middle Click |
| Short | Mouse Double Click (left) |
| C1    | Wheel Scroll Up |
| C2    | Wheel Scroll Down |

> The Dial/Knob mouse-**drag** assignments that were originally bundled here were
> too entangled to decode; drag is now its own isolated round — see **Round 8**.

## Round 6 — ✅ macro / built-in / TourMenu (samples in hand)

### `07_builtin.tb`

| Button | Built-in feature |
|--------|------------------|
| Side  | Switch Presets |
| Top   | Open/Close the D-pad HUD |
| Tall  | Open/Close the General HUD |
| Short | Open/Close Guide |

### `08_macro.tb`
- **Tall** → Macro `M1`: (1) Keystroke `X` · (2) Delay `100 ms` · (3) Keystroke `Y`.
- **Short** → Macro `M2`: (1) Text `Hello World` · (2) Mouse Move to (100,100) /
  cursor speed slow · (3) Mouse Drag from (100,100) / Delay 100 / to (200,200) /
  cursor speed fast.
- **Top** → Macro `M3`: (1) Open Folder `C:\` · (2) Open Link `www.google.com`.

### `09_tourmenu.tb`
- **Tall** → TourMenu `T1` with two items: (1) Keystroke `Z` · (2) Built-in `Switch Presets`.

---

# To do — the remaining matrix rows

## Round 5 — mode flags: UP / REP / Speed / Haptic  ▶ TBD (decode, no export)

> **Matrix row: Mode flags.** UP, REP, rotary Speed and rotary Haptic are **not
> settable on a user-created preset**, so the old "toggle one and re-export" plan
> is impossible. They *do* ship inside built-in presets, so we decode them the
> other way round: the shipped preset is the known plaintext, and we line its
> bytes up against what TourBox Console displays.

**What the data already shows.** Mode flags live in **payload byte 1** — the same
"aux" byte that is `0x04` for a built-in. Today `actions.py` sends any byte-1
value outside `{0x00, 0x04}` straight to `raw`, so these bindings round-trip
losslessly but stay opaque. Concrete examples from `samples/`:

```
CapCut  record 01:  00 10 00 00 00 00 41 ...   # key 'A' with byte1 = 0x10  (a mode flag)
CapCut  record 03:  00 10 00 00 00 00 20 ...   # Space with the same 0x10 flag
```

Speed/Haptic apply only to rotary **turn** records (type `0x08`) and likely sit in
a different byte, so they need a separate sweep of the rotary records.

**Decode plan (no new files to make):**

1. **Catalog the unknowns.** Scan every shipped `.tb` (and each `.tbg`
   sub-config) and list (a) records whose byte 1 ∉ `{0x00, 0x04}`, and
   (b) rotary records carrying bytes the current decoder can't explain. Tabulate
   the distinct flag values and which button/preset each came from.
2. **Get the plaintext from Console.** Open CapCut, Photoshop and DaVinci Resolve
   in TourBox Console and, per button, note the mode indicators shown
   (UP on/off · REP on/off · Speed level · Haptic level). Record this as a
   button → mode table — this is the ground truth we can't synthesise.

   **Fill one table per preset** (use `✓` / `–` for UP/REP; the level name or `–`
   for Speed/Haptic; `n/a` where a control can't take that mode):

   _Preset: `Photoshop.tb`_

   | Button / Control | UP | REP | Speed | Haptic | Notes |
   |------------------|----|-----|-------|--------|-------|
   | Side           |  |  | n/a | n/a |  |
   | Top            |  |  | n/a | n/a |  |
   | Tall           |  |  | n/a | n/a |  |
   | Short          |  |  | n/a | n/a |  |
   | Up (D-pad)     |  |  | n/a | n/a |  |
   | Down (D-pad)   |  |  | n/a | n/a |  |
   | Left (D-pad)   |  |  | n/a | n/a |  |
   | Right (D-pad)  |  |  | n/a | n/a |  |
   | C1             |  |  | n/a | n/a |  |
   | C2             |  |  | n/a | n/a |  |
   | Tour           |  |  | n/a | n/a |  |
   | Knob — press   |  |  | n/a | n/a |  |
   | Knob — turn    |  |  |     |     |  |
   | Scroll — press |  |  | n/a | n/a |  |
   | Scroll — turn  |  |  |     |     |  |
   | Dial — press   |  |  | n/a | n/a |  |
   | Dial — turn    |  |  |     |     |  |
3. **Correlate.** Match flag value ↔ displayed mode across the three presets. A
   given mode's encoding is the byte/bit that is constant everywhere that mode
   shows. Because we can't isolate by toggling, the multiple presets act as
   independent witnesses (e.g. confirm `0x10` is UP wherever UP is shown, and not
   present where it isn't).
4. **Implement + prove.** Add the bit/level definitions to `codes.py`; extend
   `actions.py` to surface modes on the action dict (e.g. `"mode": ["up"]` /
   `"repeat": true`, and rotary `"speed"` / `"haptic"`) *and* re-emit them on
   encode. The round-trip test proves correctness — a wrong mapping just falls
   back to `raw`, it can't corrupt a preset.

> Photoshop and CapCut are plain `.tb` (analysable directly); **DaVinci Resolve is
> a `.tbg`** holding 8 sub-config tables, which `analyze.py` can't reach yet
> (see Round 11) — extract its sub-configs first, or treat DaVinci as a
> stretch witness once `.tbg` support lands.

## Round 7 — extended keys: remaining arrows + nav + F-keys  ◑ → ✅

> **Matrix row: Extended keys.** Only ArrowUp / ArrowDown / F1 are confirmed
> (category byte = `0x01`). Fill in the rest. From-scratch presets; one unique
> extended key per button.

### `10_extkeys.tb` — arrows & navigation cluster

| Button | Key |
|--------|-----|
| Side  | Arrow Left |
| Top   | Arrow Right |
| Tall  | Home |
| Short | End |
| Up    | Page Up |
| Down  | Page Down |
| Left  | Insert |
| Right | Print Screen |

> Assign whichever of these TourBox Console offers; if one isn't available as an
> extended key, skip it and note which. (`Delete`/`Backspace` are already
> confirmed as *normal* keys in `05_specialkeys`, so don't repeat them here.)

### `10b_fkeys.tb` — function keys F2–F12

| Button | Key |
|--------|-----|
| Side  | F2 |
| Top   | F3 |
| Tall  | F4 |
| Short | F5 |
| Up    | F6 |
| Down  | F7 |
| Left  | F8 |
| Right | F9 |
| C1    | F10 |
| C2    | F11 |
| Tour  | F12 |

## Round 8 — mouse drag (isolated)  ▶ TBD

> **Matrix row: Mouse drag.** Drag uses a different action-type byte and carries
> extra option bytes (button, axis, reverse, reset-to-origin, cursor speed), so
> it round-trips as `raw` today. Decode it by flipping **one drag option per
> file** against a fixed baseline. Assign the drag to the **Dial — turn** in every
> file (a turn control, where drag belongs), changing nothing else.

### `11a_drag_base.tb`  (baseline)
Dial — turn → **Mouse Drag**: button **Left**, axis **Horizontal**, **Reverse OFF**,
**Reset-to-Origin OFF**, cursor speed **default/normal**.

| File | Change vs. `11a_drag_base` |
|------|----------------------------|
| `11b_drag_right.tb`    | button **Right** (else identical) |
| `11c_drag_vertical.tb` | axis **Vertical** |
| `11d_drag_reverse.tb`  | **Reverse ON** |
| `11e_drag_reset.tb`    | **Reset-to-Origin ON** |
| `11f_drag_speed.tb`    | cursor speed = **next setting** (e.g. Fast) |

> If the Console offers a Middle-button drag or more axis/speed options, add more
> `11…` files the same way (one option changed each).

## Round 9 — button combos  ▶ TBD

> **Matrix row: Button combos.** Holding one button while operating another
> produces a *combo*, stored in its own record code (the unmapped populated codes
> like `0x05`–`0x0E`, `0x3B`, `0xCA`–`0xCD` seen in shipped presets). To label
> them, hold **one trigger button** per file and assign a **unique key** to every
> other control reachable in combo. The diff vs. `00_base` shows which record
> codes lit up, and the key on each tells me which combo it is.

Do **one trigger per file** (this is the "one variable" rule for combos):

| File | Hold (trigger) | Then assign distinct keys to every reachable control |
|------|----------------|------------------------------------------------------|
| `12_combo_side.tb`  | **Side**  | Top, Tall, Short, the 4 D-pad dirs, C1, C2, Tour, the 3 rotary presses, the 3 rotary turns |
| `12_combo_top.tb`   | **Top**   | same set (minus Top) |
| `12_combo_tall.tb`  | **Tall**  | same set (minus Tall) |
| `12_combo_short.tb` | **Short** | same set (minus Short) |

Within each file use a simple, unique key per target so it's identifiable — e.g.
walk `A, B, C, …` down the combo list. **Tell me the exact combo → key mapping you
entered** (or just keep it consistent and I'll read it back from the diff). If the
Console exposes combos for other triggers (e.g. a D-pad or rotary held), add
`12_combo_<trigger>.tb` the same way.

## Round 10 — `<ShortDesc>` label key space  ▶ TBD

> **Matrix row: `<ShortDesc>` labels.** Custom names you type for a binding are
> stored as `<ShortDesc><m>..</m><s>..</s><d>..</d></ShortDesc>`, where `<d>` is
> the label text and `<s>` is a key whose numbering we haven't decoded (values
> exceed 255). Decode `<s>` by giving buttons with **already-known codes** (from
> Round 1) **unique labels**, then mapping each `<s>` back to its button.

### `13_labels.tb`  — from `01_simple`
Start from the `01_simple` assignments (keys `A`–`K`, so each button's record code
is already known). Then add a **distinct custom name** to each button, set to its
button name so it's unambiguous:

| Button | Key | Name (label) |
|--------|-----|--------------|
| Side  | A | `LBL-SIDE` |
| Top   | B | `LBL-TOP` |
| Tall  | C | `LBL-TALL` |
| Short | D | `LBL-SHORT` |
| Up    | E | `LBL-UP` |
| Down  | F | `LBL-DOWN` |
| Left  | G | `LBL-LEFT` |
| Right | H | `LBL-RIGHT` |
| C1    | I | `LBL-C1` |
| C2    | J | `LBL-C2` |
| Tour  | K | `LBL-TOUR` |

> **For this round, `analyze.py diff` won't help** — labels live in the XML
> envelope, not in `configBytes`. Instead dump the XML and read the `<ShortDesc>`
> block directly (see the unpack command at the bottom). I'll line each `<s>` up
> with the button whose label it carries.

## Round 11 — `.tbg` group files  (later milestone)

> **Matrix row: `.tbg`.** No new export needed — `samples/` already has real
> group files (`Lightroom.tbg`, `DaVinci Resolve.tbg`, …). DaVinci alone bundles
> **8 sub-config tables** (each 3350 B) under `<subTableTransfers>`; `analyze.py`
> only reads the first `<configBytes>`, so the prerequisite is teaching the
> container to enumerate every sub-config. Decoding `.tbg` is a later milestone
> (current tooling targets single `.tb`), and it also unblocks DaVinci as a Round 5
> mode-flag witness.

---

When files are in `samples/`, run (or ask me to run):

```bash
# Rounds 7, 8, 9 — record-level diff (the workhorse):
python tools/analyze.py diff samples/00_base.tb samples/01_simple.tb
python tools/analyze.py diff samples/11a_drag_base.tb samples/11c_drag_vertical.tb

# Round 5 (modes) — survey existing presets for unexplained byte-1 / rotary bytes:
python tools/analyze.py dump samples/CapCut.tb
python tools/analyze.py dump samples/Photoshop.tb

# Round 10 (labels) and inspecting macros/menus/.tbg sub-configs — dump the
# decoded XML instead, since analyze.py only diffs the first configBytes:
python tools/unpack.py        # writes ./dec/<name>.xml for every .tb/.tbg in cwd
```
