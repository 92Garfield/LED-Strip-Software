# 3D-printed case v1 — gLED Controller simple

Two-part case for `../../led-controller-simple.kicad_pcb`: a **tray** the PCB
screws into and a **friction-fit lid** with openings above every top-entry
connector. Outer size **90.8 × 75.8 × 34.4 mm** (tray + lid).

All geometry is parametric in `case.scad`; positions are copied from
`build_board.py` in KiCad board coordinates and mirrored automatically.

## Files

- `case.scad` — source (OpenSCAD 2021.01). `part` selects what to render:
  `"tray"`, `"lid"` (already flipped for printing) or `"assembly"`
  (tray + ghost board + hovering lid, for visual checks only).
- `case_tray.stl`, `case_lid.stl` — ready to slice, in print orientation.
- `preview_*.png` — renders of the assembly and both printable parts.

## Openings

| Where | For |
|---|---|
| Lid, right slot | J2–J5 strip plugs + wires (top-entry JST XH) |
| Lid, left slot | J7–J10 power-only plugs |
| Lid + top wall notch | J1 screw terminal: screwdriver from above, supply wires out of the top edge |
| Bottom wall slot | Pi Zero mini-HDMI / USB ports (Pi hangs under the PCB) |
| Left wall slot | Pi SD card |

## Printing

- No supports needed for either part; lid STL is already face-down.
- PLA or PETG, 0.2 mm layers, 3 perimeters. ~25 % infill is plenty.
- The lid lip has 0.3 mm clearance (`lip_clr`) — tighten/loosen to taste.

## Assembly

1. Mount the Pi on its M2.5 standoffs under the PCB (11 mm board-to-board).
2. Drop the PCB in and fasten with **4× M3 self-tapping screws** (8–10 mm)
   into the corner bosses (pilot holes Ø2.7 mm).
3. Wire J1 through the top-edge notch, plug in strips, press the lid on.

## Regenerating

```
openscad -o case_tray.stl -D "part=\"tray\"" case.scad
openscad -o case_lid.stl  -D "part=\"lid\""  case.scad
```
