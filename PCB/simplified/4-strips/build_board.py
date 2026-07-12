"""Builds led-controller-simple.kicad_pcb from scratch with the pcbnew API.

Run with KiCad's bundled python:
  "D:/Program Files/KiCad/10.0/bin/python.exe" build_board.py

Simplified variant of ../build_board.py: ONLY the Pi Zero socket, four JST
strip connectors and the 5V screw terminal. No fuses, no 74AHCT125 level
shifter, no series resistors, no capacitors -- GPIO data goes straight to
the JST data pins at 3.3 V. Board is 85 x 70 mm. Top view:

  +---------------------------------------+
  | J1   ==== +5V ====            [J2]    |
  | ||    data traces             [J3]    |
  | ||   . . . Pi header . . .    [J4]    |
  | +5V  [ Pi Zero 2 W below ]    [J5]    |
  +---------------------------------------+

Layer scheme (kept deliberately readable):
  - B.Cu: one solid GND plane, nothing else. All GND pins (J1-2, Pi
    grounds, JST pin 3) reach it through their own through-holes; no vias.
  - F.Cu: only the three +5V pours (top strip from J1, left strip to the
    Pi 5 V pins, right strip down the JST pin-1 column) plus the four data
    traces, all visible from the top.

Because all four data lines live on one layer with no crossings, the
connector rows follow the header pin order, top to bottom:
GPIO18, GPIO21, GPIO13, GPIO10 (silkscreen labels each one).
"""
import pcbnew
from pcbnew import VECTOR2I, FromMM

FP_DIR = r"D:\Program Files\KiCad\10.0\share\kicad\footprints"

def MM(x, y):
    return VECTOR2I(FromMM(x), FromMM(y))

board = pcbnew.CreateEmptyBoard()
F_Cu, B_Cu = pcbnew.F_Cu, pcbnew.B_Cu

# ---------------- nets ----------------
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]

N_5V  = net("+5V")
N_GND = net("GND")
# connector rows top->bottom; S-number = strip index in the firmware
ROWS = [  # (gpio, pi header pin, firmware strip name)
    (18, 12, "S1"),
    (21, 40, "S4"),
    (13, 33, "S2"),
    (10, 19, "S3"),
]
N_DATA = [net(f"DATA_GPIO{g}") for (g, _, _) in ROWS]

# ---------------- helpers ----------------
def place(lib, name, ref, x, y, rot=0.0, flip=False, value=""):
    fp = pcbnew.FootprintLoad(FP_DIR + "\\" + lib + ".pretty", name)
    if fp is None:
        raise RuntimeError(f"footprint not found: {lib}/{name}")
    fp.SetReference(ref)
    if value:
        fp.SetValue(value)
    board.Add(fp)
    if flip:
        fp.Flip(MM(x, y), False)
    fp.SetPosition(MM(x, y))
    fp.SetOrientationDegrees(rot)
    return fp

def setnets(fp, mapping):
    for pad in fp.Pads():
        n = mapping.get(pad.GetNumber())
        if n is not None:
            pad.SetNet(n)

def padpos(fp, num):
    for pad in fp.Pads():
        if pad.GetNumber() == str(num):
            p = pad.GetPosition()
            return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
    raise RuntimeError(f"{fp.GetReference()} has no pad {num}")

def solve_placement(fp, targets):
    """Rotate/translate fp so numbered pads land on target (x, y) points."""
    first = sorted(targets)[0]
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        p1 = fp.FindPadByNumber(str(first)).GetPosition()
        ref = fp.GetPosition()
        t1 = MM(*targets[first])
        fp.SetPosition(VECTOR2I(ref.x + (t1.x - p1.x), ref.y + (t1.y - p1.y)))
        if all(abs(padpos(fp, n)[0] - t[0]) < 0.01 and
               abs(padpos(fp, n)[1] - t[1]) < 0.01
               for n, t in targets.items()):
            return rot
    raise RuntimeError(f"cannot orient {fp.GetReference()} onto targets")

def track(pts, netitem, width, layer=F_Cu):
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(MM(*a)); t.SetEnd(MM(*b))
        t.SetWidth(FromMM(width)); t.SetLayer(layer); t.SetNet(netitem)
        board.Add(t)

def zone(outline_mm, netitem, layer, priority=0, min_w=0.25, solid=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer); z.SetNet(netitem)
    z.SetAssignedPriority(priority)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid
                       else pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetLocalClearance(FromMM(0.3))
    z.SetMinThickness(FromMM(min_w))
    z.SetThermalReliefGap(FromMM(0.5))
    z.SetThermalReliefSpokeWidth(FromMM(1.0))
    pts = pcbnew.VECTOR_VECTOR2I()
    for (x, y) in outline_mm:
        pts.append(MM(x, y))
    z.AddPolygon(pts)
    board.Add(z)
    return z

def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def edge_line(a, b):
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(MM(*a)); s.SetEnd(MM(*b))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
    board.Add(s)

def silk(text, x, y, size=1.2, layer=None, angle=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(MM(x, y))
    t.SetLayer(layer if layer is not None else pcbnew.F_SilkS)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(angle)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)

# --- geometry constants (mm) ---
W, H = 85.0, 70.0
PI_X, PI_Y = 8.0, 36.0              # Pi Zero top-left corner (65 x 30)
HDR_Y = PI_Y + 3.5                  # header / mount-hole line = 39.5
PIN1_X = PI_X + 32.5 - 9.5 * 2.54   # leftmost header column = 16.37
JX = 77.0                           # JST pin-1 column (courtyard clears H2/H4)
JY = [11.5 + 14 * i for i in range(4)]   # JST pin-1 rows

# ---------------- components ----------------
j1 = place("TerminalBlock_Phoenix",
           "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal",
           "J1", 13.0, 8.0, rot=0, value="5V IN")
setnets(j1, {"1": N_5V, "2": N_GND})

jst = []
for i, (g, _, s) in enumerate(ROWS):
    j = place("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
              f"J{i+2}", JX, JY[i], rot=270, value=f"GPIO{g}")
    setnets(j, {"1": N_5V, "2": N_DATA[i], "3": N_GND})
    jst.append(j)

# J6 socket on the back, holes aligned with the Pi header below
j6 = place("Connector_PinSocket_2.54mm", "PinSocket_2x20_P2.54mm_Vertical",
           "J6", 50.0, 50.0, rot=0, flip=True, value="Pi Zero 2 WH")

def pi_pin_xy(n):
    col = (n - 1) // 2
    x = PIN1_X + 2.54 * col
    y = HDR_Y + 1.27 if n % 2 == 1 else HDR_Y - 1.27
    return (x, y)

solve_placement(j6, {n: pi_pin_xy(n) for n in (1, 2, 39, 40)})
m = {str(n): N_5V for n in (2, 4)}
m.update({str(n): N_GND for n in (6, 9, 14, 20, 25, 30, 34, 39)})
m.update({str(pin): N_DATA[i] for i, (_, pin, _) in enumerate(ROWS)})
setnets(j6, m)

mh = 1
for (x, y) in [(PI_X + 3.5, HDR_Y), (PI_X + 61.5, HDR_Y),
               (PI_X + 3.5, PI_Y + 26.5), (PI_X + 61.5, PI_Y + 26.5)]:
    place("MountingHole", "MountingHole_2.7mm_M2.5", f"H{mh}", x, y).Reference().SetVisible(False)
    mh += 1
for (x, y) in [(4, 4), (81, 4), (4, 66), (81, 66)]:
    place("MountingHole", "MountingHole_3.2mm_M3", f"H{mh}", x, y).Reference().SetVisible(False)
    mh += 1

# ---------------- board outline ----------------
edge_line((0, 0), (W, 0)); edge_line((W, 0), (W, H))
edge_line((W, H), (0, H)); edge_line((0, H), (0, 0))

# ---------------- zones ----------------
# Back: one solid GND plane over the whole board, nothing else on B.Cu.
zone(rect(0, 0, W, H), N_GND, B_Cu, priority=0)
# Front: ONLY the +5V areas -- everything copper you see on top is +5V.
zone(rect(0, 0, 83.0, 12.0), N_5V, F_Cu, priority=3)   # top strip from J1
zone(rect(0, 0, 20.2, 44.0), N_5V, F_Cu, priority=2)   # left strip -> Pi 5V
zone(rect(74.0, 0, 83.0, 58.0), N_5V, F_Cu, priority=1)  # right strip -> JST pin 1

# ---------------- routing (all data on F.Cu, no crossings) ----------------
PIN = {pin: pi_pin_xy(pin) for (_, pin, _) in ROWS}
D = {JY[i] + 2.5: N_DATA[i] for i in range(4)}   # JST data-pad rows: 14/28/42/56
# GPIO18: Pi pin12 (top row) straight up, then right into J2 pin 2
track([PIN[12], (29.07, 14.0), (JX, 14.0)], N_DATA[0], 0.5)
# GPIO21: Pi pin40 (rightmost, top row) up, then right into J3 pin 2
track([PIN[40], (64.63, 28.0), (JX, 28.0)], N_DATA[1], 0.5)
# GPIO13: Pi pin33 (bottom row) short dodge below the header into J4 pin 2
track([PIN[33], (58.28, 42.3), (75.0, 42.3), (JX, 42.0)], N_DATA[2], 0.5)
# GPIO10: Pi pin19 (bottom row) down between columns, along the Pi, into J5
track([PIN[19], (40.5, 42.04), (40.5, 56.0), (JX, 56.0)], N_DATA[3], 0.5)

# ---------------- silkscreen ----------------
silk("gLED Controller simple", 40, 3.5, 2.0)
silk("5V IN", 15.5, 17.8, 1.0)
silk("+", 13.0, 15.4, 1.5); silk("-", 18.08, 15.4, 1.5)
silk("NO FUSES - FUSE SUPPLY EXTERNALLY", 40, 17.5, 1.0)
silk("3V3 DATA - KEEP STRIP LEADS SHORT", 40, 20.5, 1.0)
silk("GND = SOLID PLANE ON BOTTOM", 40, 23.5, 1.0)
silk("+5V", 50.0, 8.0, 1.5)
silk("+5V", 10.0, 30.0, 1.5, angle=90)
silk("+5V", 80.8, 33.0, 1.5, angle=90)
for i, (g, _, s) in enumerate(ROWS):
    silk(f"{s} GPIO{g}", 62.5, JY[i] + 7.3, 1.0)
    silk("+", JX - 4.5, JY[i], 1.0)
    silk("D", JX - 4.5, JY[i] + 2.5, 1.0)
    silk("G", JX - 4.5, JY[i] + 5.0, 1.0)
silk("Pi Zero 2 WH under board, pins up", 40.5, 51, 1.2, pcbnew.B_SilkS)
silk("GND PLANE", 40, 25, 2.0, pcbnew.B_SilkS)

# Pi outline on back silk as orientation aid
for a, b in [((PI_X, PI_Y), (PI_X + 65, PI_Y)),
             ((PI_X + 65, PI_Y), (PI_X + 65, PI_Y + 30)),
             ((PI_X + 65, PI_Y + 30), (PI_X, PI_Y + 30)),
             ((PI_X, PI_Y + 30), (PI_X, PI_Y))]:
    s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(MM(*a)); s.SetEnd(MM(*b))
    s.SetLayer(pcbnew.B_SilkS); s.SetWidth(FromMM(0.15))
    board.Add(s)

# ---------------- save (zones filled in a separate pass) ----------------
board.Save("led-controller-simple.kicad_pcb")
print("board written: led-controller-simple.kicad_pcb")
