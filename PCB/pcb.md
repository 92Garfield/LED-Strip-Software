# LED Controller PCB — KiCad files

Carrier board for a Raspberry Pi Zero 2 WH: 110 × 70 mm, 2 layers, 2 oz copper.
The board sits **on top of** the Pi like an oversized pHAT — the 2×20 socket is
on the back side, the Pi hangs underneath on M2.5 standoffs with its pins
pointing up into the socket. Design intent and part choices are in `plan.md`;
this file explains what each generated file is and what it means electrically.

## Source files

### `build_board.py`
The actual "source code" of the board. Running it with KiCad's bundled Python
regenerates `led-controller.kicad_pcb` from scratch — every footprint position,
net assignment, trace, zone and silkscreen label is defined here as code.
If you want to change the layout, change this script, not the `.kicad_pcb`
(manual edits in KiCad get overwritten on the next script run).

```
"D:/Program Files/KiCad/10.0/bin/python.exe" build_board.py
"D:/Program Files/KiCad/10.0/bin/python.exe" fill_zones.py
```

Electrically, the script defines these nets:

| Net | Meaning |
|---|---|
| `+5V` | Raw supply from J1. Feeds the Pi (header pins 2/4), U1's VCC, and all four fuse inputs. Distributed as wide copper pours, not traces, because worst case is ~20 A. |
| `GND` | Common return. Poured on both layers, stitched with vias. |
| `5V_S1`…`5V_S4` | The four **fused** 5 V outputs — everything after fuse Fx belongs to its own net so a blown fuse isolates exactly one strip. |
| `D18_3V3`, `D13_3V3`, `D10_3V3`, `D21_3V3` | 3.3 V logic from the Pi GPIOs (18/13/10/21) into the level shifter inputs. |
| `D1_5V`…`D4_5V` | 5 V logic out of the 74AHCT125, before the series resistor. |
| `DATA1`…`DATA4` | After the 470 Ω resistor, into JST pin 2 — what the first LED of each strip sees. |

Channel mapping (matches `plan.md` and the firmware): GPIO18 → S1/J2,
GPIO13 → S2/J3, GPIO10 → S3/J4, GPIO21 → S4/J5.

### `fill_zones.py`
Refills the copper zones after a rebuild. Separate script because KiCad's zone
filler crashes when called on a freshly built in-memory board (standalone
Python quirk) — it must load the saved file, fill, and save again. **Zones must
be filled** before export: unfilled zones would mean the Gerbers contain no
+5V/GND copper at all.

## Board files

### `led-controller.kicad_pcb`
The board itself — open this in KiCad (PCB Editor) to inspect or measure.
Layout, electrically:

- **Front (F.Cu), +5V pours**: a top strip from J1 across the board, a left
  strip feeding the Pi's 5 V pins, and a ~12 mm vertical bus feeding all four
  fuse inputs. Sized for 20 A total at 2 oz copper; the bus connects to the
  fuse clips solid (no thermal spokes) to minimize resistance.
- **Fuse rows**: each 5×20 mm fuse lies directly in line with its JST
  connector, so the fused current path is fuse clip → 2 mm trace → JST pin 1,
  a few millimetres long. No fused current crosses the rest of the board.
- **Data path**: Pi GPIO (through-hole header pads) → short front-side traces
  → 74AHCT125 inputs. The shifted 5 V outputs run on the **back** layer to the
  470 Ω resistors (also mounted on the back, next to the JSTs) → JST pin 2.
  Resistors sit close to the connectors on purpose: they damp reflections at
  the cable, which only works near the line's driving end.
- **GND**: full pours on both layers plus ~20 stitching vias. LED return
  current flows from JST pin 3 through these planes back to J1. The unused
  74AHCT125 enable pins (1, 4, 10, 13) are tied to GND via the back pour —
  outputs permanently enabled.
- **Mounting**: H1–H4 are the M2.5 Pi-pattern holes (58 × 23 mm), H5–H8 are M3
  case-mounting corner holes. All holes are unplated and carry no net.

### `led-controller.kicad_pro` / `.kicad_prl` / `~*.lck`
KiCad project settings, per-user display state, and an editor lock file.
No electrical content; the `.lck` just means the board is open in KiCad.
None of these are needed for manufacturing.

## Manufacturing outputs

### `gerbers/` and `led-controller-gerbers.zip`
The zip is what you upload to the fab (JLCPCB etc.) — it contains exactly the
files in `gerbers/`. Gerbers are the fab's ground truth; they describe
photomask geometry per layer, with no nets or components:

| File | Layer | Electrical meaning |
|---|---|---|
| `*-F_Cu.gtl` | Front copper | All top-side conductors: +5V pours, fused-output traces, data input traces, GND fill. |
| `*-B_Cu.gbl` | Back copper | Bottom conductors: GND plane, level-shifter output traces, resistor connections. |
| `*-F_Mask.gts` / `*-B_Mask.gbs` | Solder mask | *Openings* in the green coating — where copper is exposed for soldering. Everything else stays insulated. |
| `*-F_Silkscreen.gto` / `*-B_Silkscreen.gbo` | Silkscreen | Ink only, no electrical function: reference designators, `+`/`−` polarity at J1, `+`/`D`/`G` pinout at each JST, fuse ratings, Pi placement outline on the back. |
| `*-Edge_Cuts.gm1` | Board outline | Where the board is routed out — the 110 × 70 mm contour. |
| `*.drl` | Excellon drill | Every hole: plated through-holes (component pins and vias, walls metallized so they conduct between layers) and the non-plated mounting holes. |
| `*-drl_map.gbr`, `*-job.gbrjob` | Drill map / job file | Documentation for the fab; no copper. |

**Ordering note:** select **2 oz outer copper**. The pour widths were sized for
that; at standard 1 oz the +5V distribution would run roughly twice as warm.

### `bom.csv`
Parts list with LCSC part numbers, JLCPCB BOM format. Quantities note: 8 fuse
clips (2 per position); the 5 A glass fuses themselves are bought separately.
U1 is listed as the hand-solderable DIP — swap to SN74AHCT125DR (SOIC-14) if
ordering assembly.

## Verification artifacts

- `drc.json` — last design-rule-check report: **0 errors, 0 unconnected
  items** (remaining warnings are silkscreen cosmetics). Regenerate with
  `kicad-cli pcb drc --format json --output drc.json led-controller.kicad_pcb`.
- `render_top.png` / `render_bottom.png` — 3D renders for a quick visual check
  without opening KiCad.

## Regenerating everything

```
cd PCB
"D:/Program Files/KiCad/10.0/bin/python.exe" build_board.py
"D:/Program Files/KiCad/10.0/bin/python.exe" fill_zones.py
kicad-cli pcb drc --format json --output drc.json led-controller.kicad_pcb
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts --subtract-soldermask --output gerbers/ led-controller.kicad_pcb
kicad-cli pcb export drill --format excellon --drill-origin absolute --generate-map --map-format gerberx2 --output gerbers/ led-controller.kicad_pcb
```

Close the board in KiCad first — the build overwrites `led-controller.kicad_pcb`.
