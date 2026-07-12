# LED Controller PCB — simplified variant

Bare-minimum version of `../led-controller.kicad_pcb` for hand assembly:
**only** the 5 V screw terminal (J1), four JST strip connectors (J2–J5) and
the 2×20 socket for the Pi Zero 2 WH (J6). 85 × 70 mm, 2 layers, 2 oz copper.
Same carrier concept as the full board: the socket sits on the **back**, the
Pi hangs underneath on M2.5 standoffs with its pins pointing up into it.

Only 6 solder parts, all through-hole — a 15-minute soldering job.

## Deliberately readable layout

The copper is arranged so you can verify everything by eye from the renders:

- **Back layer = one solid GND plane, nothing else.** No traces, no vias.
  Every GND pin (J1 pin 2, the Pi's ground pins, each JST `G` pin) reaches
  the plane through its own through-hole.
- **Front layer = only +5V areas + the four data traces.** Any copper you
  see on top is +5V: a top strip from J1, a left strip feeding the Pi's 5 V
  pins (header pins 2/4), and a right strip feeding every JST `+` pin.
  Each area carries a `+5V` silkscreen label.
- **All four data traces run on the front**, GPIO pin → JST `D` pin, fully
  visible, no layer changes, no crossings.

Routing all data on one side without crossings forces the connector order
to follow the header pin geometry. Top to bottom the connectors are:

| Connector | GPIO | Pi header pin | Firmware strip |
|---|---|---|---|
| J2 (top) | GPIO18 | 12 | S1 |
| J3 | GPIO21 | 40 | S4 |
| J4 | GPIO13 | 33 | S2 |
| J5 (bottom) | GPIO10 | 19 | S3 |

Note this is **not** S1→S4 in order — each connector's silkscreen states its
GPIO and strip number, so plug strips by label, not by position.

## What was removed vs. the full board, and what that means

| Removed | Consequence |
|---|---|
| Fuses F1–F4 | JST `+` pins are fed **directly** from the +5V pour. A short in a strip or cable is limited only by your PSU. Put a fuse in the supply wire before J1 (or use a PSU with proper overcurrent protection). |
| 74AHCT125 level shifter | Data pins carry **3.3 V logic straight from the GPIOs** into nominally-5 V strips. WS2812B usually accept this when the data lead is short (< ~1 m) and power/ground are solid. If a strip glitches, shorten the lead or drop strip VCC slightly (e.g. one diode) — or use the full board. |
| 470 Ω series resistors | No reflection damping at the cable. Another reason to keep strip leads short. |
| 1000 µF bulk cap + 100 nF | Add a bulk electrolytic at the strip or PSU end if you see flicker on load steps. |

## Files

- `build_board.py` — the source of truth; regenerates the `.kicad_pcb` from
  scratch (same workflow as the full board, see `../pcb.md`).
- `fill_zones.py` — refills copper zones after a rebuild (must run, or the
  Gerbers contain no +5V/GND copper).
- `led-controller-simple.kicad_pcb` — the board; open in KiCad to inspect.
- `gerbers/`, `led-controller-simple-gerbers.zip` — upload the zip to the fab.
- `drc.json` — DRC report: **0 errors, 0 warnings, 0 unconnected items**.
- `render_top.png` / `render_bottom.png` — 3D renders.
- `bom.csv` — the three connector types (plus standoffs).

## Regenerating

```
cd PCB/simplified
"D:/Program Files/KiCad/10.0/bin/python.exe" build_board.py
"D:/Program Files/KiCad/10.0/bin/python.exe" fill_zones.py
kicad-cli pcb drc --format json --output drc.json led-controller-simple.kicad_pcb
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts --subtract-soldermask --output gerbers/ led-controller-simple.kicad_pcb
kicad-cli pcb export drill --format excellon --drill-origin absolute --generate-map --map-format gerberx2 --output gerbers/ led-controller-simple.kicad_pcb
```

**Ordering note:** still select **2 oz outer copper** — the +5V pours are
sized for ~20 A total at 2 oz.
