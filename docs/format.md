# TourBox `.tb` / `.tbg` file format

This is the reverse-engineered specification the library is built on.

## 1. Container (fully solved)

```
.tb file  =  gzip( XStream-XML )
```

- **gzip**: files start with magic `1F 8B 08`. Decompress to get UTF-8 XML.
- **XML**: XStream-serialized Java object, root `<TableTransfer>`, `<version>1.8</version>`.
- Key elements:
  - `<configBytes>` — base64 of the binary **binding table** (see §2).
  - `<shortCuts>` / `<ShortDesc>` — sparse human labels (see §3).
  - `<macros>`, `<hudList>`, `<menus>` — supporting config, preserved verbatim by the encoder.

`tbtool` only rewrites `<configBytes>`; everything else is copied from a base envelope.

## 2. Binding table (`configBytes`)

Decoded size is always **3350 bytes**:

```
+--------------------+-------------------------------------------------+
| header: 22 bytes   | 256 records x 13 bytes                          |
+--------------------+-------------------------------------------------+

record[code]  (13 bytes), for code = 0x00 .. 0xFF
  byte 0      : == code  (self-referential index; encoder re-asserts this)
  byte 1..12  : 12-byte action payload (all zero => button unassigned)
```

- The 22-byte header is opaque; its first bytes vary between files. We preserve it.
- Only ~51 codes are ever populated across the shipped presets (a contiguous
  `0x00–0x25` block plus rotary/combo clusters), consistent with the Elite's
  buttons + combinations.

## 3. Action payload (partially decoded — see `docs/calibration.md`)

12 bytes. Offsets below are **0-based within the payload** (so payload byte 6 =
record byte 7).

| Field | Offset | Status | Notes |
|-------|--------|--------|-------|
| action-type | 0 | ✅ partial | bitfield. `0x00`=single key, `0x08`=two-way rotary (dominant). Also seen `0x04/0x05/0x09/0x0A` (mouse/wheel/mode — ▶TBD). |
| key code (dir 1) | 6 | ✅ for letters/digits/space | VK-style; equals ASCII upper for `A–Z`/`0–9`. e.g. `45`=E, `20`=Space. |
| key code (dir 2) | 11 | ✅ for rotary | second direction of a two-way control. e.g. `[`=`5B`, `]`=`5D`. |
| modifier bits | ~2–3 | ▶ TBD | a pure `Alt` binding sets payload byte 2 to `0x02`; full bitmask & byte unconfirmed. |
| mouse / wheel | — | ▶ TBD | encoded under non-zero action-type values. |
| mode flags (UP/REP/Speed/Haptic) | — | ▶ TBD | manual §5. |

### How `tbtool` stays lossless despite the unknowns

`actions.decode_action` only emits a semantic form (`key`, `rotary`) when
re-encoding it reproduces the **exact** original bytes. Anything else is kept as
`{"type": "raw", "hex": "..."}`. So every preset round-trips byte-for-byte today,
and semantic coverage grows safely as calibration confirms more fields.

## 4. `<ShortDesc>` labels

```xml
<ShortDesc><m>0</m><s>66</s><d>Volumn Up</d></ShortDesc>
```

`<d>` is the user label. `<s>` is **not** the `configBytes` index (observed values
exceed 255, e.g. `16777223`), so labels are currently surfaced informationally as
`shortcutLabels` in the JSON and inherited from the base envelope on encode. Decoding
the `<s>` key space is a calibration task.

## 5. `.tbg` group files

Same gzip→XML envelope, but bundle multiple configs under `<subTableTransfers>`
plus a `<presetConf>` documentation tree (HTML guides) and `<menus>` radial menus.
The top-level `configBytes` is empty; the real tables live in the sub-configs.
`tbtool` v1 targets single `.tb` files; `.tbg` is a later milestone.
