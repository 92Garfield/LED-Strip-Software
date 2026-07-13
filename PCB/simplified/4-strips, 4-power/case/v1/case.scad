// 3D-printable case for "gLED Controller simple" (led-controller-simple.kicad_pcb)
// -------------------------------------------------------------------------------
// Two parts: a TRAY the PCB screws into (M3 self-tapping into corner bosses,
// same holes H5-H8 the board already has) and a friction-fit LID with openings
// above every top-entry connector.
//
// The Pi Zero 2 WH hangs UNDER the PCB (socket on the PCB back, Pi on M2.5
// standoffs), so the tray provides 16 mm of depth below the board plus port /
// SD-card openings in the lower walls.
//
// All positions are taken from build_board.py and entered in KICAD board
// coordinates (origin at board top-left, y pointing DOWN). The krect() helper
// flips y so the printed case matches the physical board.
//
// Render:
//   part = "tray"      -> printable tray (prints as modeled, no supports)
//   part = "lid"       -> printable lid  (already flipped flat on the bed)
//   part = "assembly"  -> tray + ghost board + lid hovering (visual check only)

part = "assembly";

// ---------------- board facts (kicad coords, mm) ----------------
W  = 85;      // board size
H  = 70;
PCB_T = 1.6;

M3_HOLES = [[4, 4], [81, 4], [4, 66], [81, 66]];   // H5-H8

JY = [11.5, 25.5, 39.5, 53.5];   // JST pin-1 rows (both columns)
// JST XH body bounding boxes (from footprint courtyard, minus its 0.25 margin)
JST_R = [73.3, 79.6];            // right column J2-J5, body x-range
JST_L = [1.8, 8.15];             // left column J7-J10, body x-range
JST_DY = [-2.7, 7.7];            // body y-range relative to pin-1 row
JST_HT = 7.0;                    // body height above PCB

J1_BOX = [37.1, 1.8, 47.9, 13.6];  // terminal block body x0,y0,x1,y1
J1_HT  = 10.3;

// Pi Zero 2 WH under the board: top face 11 mm below PCB bottom
PI_BOX  = [8, 36, 73, 66];       // outline in board coords
PI_DROP = 11;                    // PCB bottom -> Pi component face
PI_T    = 1.6;
// port centers on the Pi edge that faces the board's bottom edge (y = 70):
// mini-HDMI x=20.4, USB-OTG x=49.4, USB-PWR x=62 (board coords)

// ---------------- case parameters ----------------
clr     = 0.5;    // gap board edge -> inner wall
wall    = 2.4;
floor_t = 2.4;
below   = 16;     // interior floor -> PCB bottom (socket 8.5 + Pi 11+1.6 + air)
above   = 12;     // PCB top -> wall top (J1 is 10.3 tall)
boss_d  = 7;
pilot_d = 2.7;    // M3 self-tapping
pilot_depth = 9;

lid_t   = 2.4;
lip_h   = 3;      // friction lip reaching into the tray
lip_w   = 2;
lip_clr = 0.3;    // lip -> inner wall clearance

$fn = 48;

// ---------------- derived ----------------
pcb_bot  = below;            // z of PCB underside (z=0 = interior floor)
pcb_top  = below + PCB_T;
wall_top = pcb_top + above;

ix0 = -clr;      ix1 = W + clr;      // interior cavity
iy0 = -clr;      iy1 = H + clr;
ox0 = ix0 - wall; ox1 = ix1 + wall;  // outer shell
oy0 = iy0 - wall; oy1 = iy1 + wall;

echo(str("outer size: ", ox1 - ox0, " x ", oy1 - oy0, " x ",
         floor_t + wall_top + lid_t, " mm (tray + lid)"));

// cube from kicad-coordinate corners (flips y), z absolute
module krect(x0, y0, x1, y1, z0, z1) {
    translate([x0, H - y1, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

// ---------------- tray ----------------
module tray() {
    difference() {
        union() {
            // shell with floor, cavity carved out
            difference() {
                translate([ox0, H - iy1 - wall, -floor_t])
                    cube([ox1 - ox0, oy1 - oy0, floor_t + wall_top]);
                krect(ix0, iy0, ix1, iy1, 0, wall_top + 1);
            }
            // corner bosses the PCB screws onto
            for (p = M3_HOLES)
                translate([p[0], H - p[1], 0]) cylinder(d = boss_d, h = below);
        }
        // J1 wire/screwdriver notch, wall at the board's top edge
        krect(35.5, -clr - wall - 1, 49.5, 1, pcb_top, wall_top + 1);
        // Pi port slot (mini-HDMI / USB), wall at the board's bottom edge
        krect(14, H - 1, 70, H + clr + wall + 1, 3.5, 14.5);
        // SD-card slot, left wall
        krect(-clr - wall - 1, 41, 1, 61, 3.5, 14.5);
        // pilot holes in the bosses
        for (p = M3_HOLES)
            translate([p[0], H - p[1], below - pilot_depth])
                cylinder(d = pilot_d, h = pilot_depth + 1);
    }
}

// ---------------- lid (modeled in mounted position) ----------------
module lid_in_place() {
    difference() {
        union() {
            translate([ox0, H - iy1 - wall, wall_top])
                cube([ox1 - ox0, oy1 - oy0, lid_t]);
            // friction lip
            translate([0, 0, wall_top - lip_h]) linear_extrude(lip_h)
                difference() {
                    translate([ix0 + lip_clr, H - iy1 + lip_clr])
                        square([(ix1 - ix0) - 2 * lip_clr,
                                (iy1 - iy0) - 2 * lip_clr]);
                    translate([ix0 + lip_clr + lip_w, H - iy1 + lip_clr + lip_w])
                        square([(ix1 - ix0) - 2 * (lip_clr + lip_w),
                                (iy1 - iy0) - 2 * (lip_clr + lip_w)]);
                }
        }
        // opening above right JST column (J2-J5, strip plugs + wires)
        krect(JST_R[0] - 1.3, JY[0] + JST_DY[0] - 1.3, JST_R[1] + 1.3,
              JY[3] + JST_DY[1] + 1.3, wall_top - lip_h - 1, wall_top + lid_t + 1);
        // opening above left JST column (J7-J10, power plugs). Cut from x=-1,
        // all the way through the lip: the connectors sit so close to the board
        // edge that stopping at the body would leave a 0.7 mm lip sliver.
        krect(-1, JY[0] + JST_DY[0] - 1.3, JST_L[1] + 1.3,
              JY[3] + JST_DY[1] + 1.3, wall_top - lip_h - 1, wall_top + lid_t + 1);
        // J1 access: open to the board edge so supply wires drop in
        krect(35.5, -clr - wall - 2, 49.5, 15, wall_top - lip_h - 1,
              wall_top + lid_t + 1);
    }
}

// lid flipped flat on the print bed (top face down)
module lid_print() {
    translate([0, 0, wall_top + lid_t]) rotate([180, 0, 0]) lid_in_place();
}

// ---------------- ghost board for the assembly view ----------------
module board_ghost() {
    color("darkgreen", 0.85) krect(0, 0, W, H, pcb_bot, pcb_top);
    color("limegreen", 0.9)                        // J1 terminal block
        krect(J1_BOX[0], J1_BOX[1], J1_BOX[2], J1_BOX[3],
              pcb_top, pcb_top + J1_HT);
    color("white", 0.9) for (y = JY) {             // 8x JST XH
        krect(JST_R[0], y + JST_DY[0], JST_R[1], y + JST_DY[1],
              pcb_top, pcb_top + JST_HT);
        krect(JST_L[0], y + JST_DY[0], JST_L[1], y + JST_DY[1],
              pcb_top, pcb_top + JST_HT);
    }
    color("dimgray", 0.9)                          // 2x20 socket on the back
        krect(13.5, 36.5, 67.5, 42.5, pcb_bot - 8.5, pcb_bot);
    color("forestgreen", 0.85)                     // Pi Zero 2 WH
        krect(PI_BOX[0], PI_BOX[1], PI_BOX[2], PI_BOX[3],
              pcb_bot - PI_DROP - PI_T, pcb_bot - PI_DROP);
}

// ---------------- part selection ----------------
if (part == "tray") tray();
if (part == "lid") lid_print();
if (part == "assembly") {
    tray();
    board_ghost();
    color("steelblue", 0.45) translate([0, 0, 12]) lid_in_place();
}
