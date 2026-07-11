"""Builds led-controller.kicad_pcb from scratch with the pcbnew API.

Run with KiCad's bundled python:
  "D:/Program Files/KiCad/10.0/bin/python.exe" build_board.py

Board concept (see pcb.md): carrier that sits ON TOP of a Pi Zero 2 WH
(socket J6 on the back side, Pi below, M2.5 standoffs). Top view:

  +----------------------------------------------------------+
  | J1                                    F1 =fuse=  [J2]    |
  | C1        U1                          F2 =fuse=  [J3]    |
  |          74AHCT125    | +5V |         F3 =fuse=  [J4]    |
  |     . . . Pi header . | bus |. .      F4 =fuse=  [J5]    |
  |  o    [ Pi Zero 2 W below, 65x30 ]  o                    |
  +----------------------------------------------------------+

Power: +5V pours (front) top strip + left strip + vertical bus feeding the
fuse inputs; each fuse output runs straight into its JST. GND is poured on
both layers. Data: Pi GPIO -> U1 inputs on the front, U1 outputs -> R (back
side) -> JST data pins on the back layer.
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

N_5V   = net("+5V")
N_GND  = net("GND")
N_5V_S = [net(f"5V_S{i}") for i in (1, 2, 3, 4)]          # fused strip supplies
N_GPIO = [net(n) for n in ("D18_3V3", "D13_3V3", "D10_3V3", "D21_3V3")]
N_D5V  = [net(f"D{i}_5V") for i in (1, 2, 3, 4)]          # buffer out -> resistor
N_DATA = [net(f"DATA{i}") for i in (1, 2, 3, 4)]          # resistor -> JST

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

def via(x, y, netitem, size=0.8, drill=0.4):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(MM(x, y))
    v.SetWidth(FromMM(size)); v.SetDrill(FromMM(drill))
    v.SetLayerPair(F_Cu, B_Cu); v.SetNet(netitem)
    board.Add(v)

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
W, H = 110.0, 70.0
PI_X, PI_Y = 8.0, 36.0              # Pi Zero top-left corner (65 x 30)
HDR_Y = PI_Y + 3.5                  # header / mount-hole line = 39.5
PIN1_X = PI_X + 32.5 - 9.5 * 2.54   # leftmost header column = 16.37
JY = [11.5 + 14 * i for i in range(4)]   # JST pin-1 / fuse rows

# ---------------- components ----------------
j1 = place("TerminalBlock_Phoenix",
           "TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal",
           "J1", 13.0, 8.0, rot=0, value="5V IN")
setnets(j1, {"1": N_5V, "2": N_GND})

c1 = place("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C1", 6.5, 22.0,
           rot=270, value="1000uF 16V")
setnets(c1, {"1": N_5V, "2": N_GND})

fuses = []
for i in range(4):
    f = place("Fuse",
              "Fuseholder_Clip-5x20mm_Littelfuse_520_Inline_P20.50x5.80mm_D1.30mm_Horizontal",
              f"F{i+1}", 74.5, JY[i], rot=0, value="5A")
    setnets(f, {"1": N_5V, "2": N_5V_S[i]})
    fuses.append(f)

# U1 horizontal DIP: pin1 bottom-left (38.38, 27.62), pin14 top-left (38.38, 20)
u1 = place("Package_DIP", "DIP-14_W7.62mm", "U1", 46.0, 23.8, rot=0,
           value="74AHCT125")
u1rot = solve_placement(u1, {1: (38.38, 27.62), 7: (53.62, 27.62),
                             14: (38.38, 20.0), 8: (53.62, 20.0)})
setnets(u1, {
    "1": N_GND, "2": N_GPIO[0], "3": N_D5V[0],     # gate A: D18 -> ch1 (J2)
    "4": N_GND, "5": N_GPIO[2], "6": N_D5V[2],     # gate B: D10 -> ch3 (J4)
    "7": N_GND,
    "8": N_D5V[3], "9": N_GPIO[3], "10": N_GND,    # gate C: D21 -> ch4 (J5)
    "11": N_D5V[1], "12": N_GPIO[1], "13": N_GND,  # gate D: D13 -> ch2 (J3)
    "14": N_5V,
})

c2 = place("Capacitor_SMD", "C_0805_2012Metric", "C2", 33.0, 21.8, rot=0,
           value="100nF")
setnets(c2, {"1": N_5V, "2": N_GND})

jst = []
for i in range(4):
    j = place("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
              f"J{i+2}", 101.0, JY[i], rot=270, value=f"STRIP{i+1}")
    setnets(j, {"1": N_5V_S[i], "2": N_DATA[i], "3": N_GND})
    jst.append(j)

rs = []
for i in range(4):
    r = place("Resistor_SMD", "R_0805_2012Metric", f"R{i+1}", 98.2, JY[i] + 2.5,
              rot=0, flip=True, value="470R")
    setnets(r, {"1": N_D5V[i], "2": N_DATA[i]})
    rs.append(r)

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
m.update({"12": N_GPIO[0], "33": N_GPIO[1], "19": N_GPIO[2], "40": N_GPIO[3]})
setnets(j6, m)

mh = 1
for (x, y) in [(PI_X + 3.5, HDR_Y), (PI_X + 61.5, HDR_Y),
               (PI_X + 3.5, PI_Y + 26.5), (PI_X + 61.5, PI_Y + 26.5)]:
    place("MountingHole", "MountingHole_2.7mm_M2.5", f"H{mh}", x, y); mh += 1
for (x, y) in [(4, 4), (106, 4), (4, 66), (106, 66)]:
    place("MountingHole", "MountingHole_3.2mm_M3", f"H{mh}", x, y); mh += 1

# ---------------- board outline ----------------
edge_line((0, 0), (W, 0)); edge_line((W, 0), (W, H))
edge_line((W, H), (0, H)); edge_line((0, H), (0, 0))

# ---------------- zones ----------------
# GND both sides, lowest priority
zone(rect(0, 0, W, H), N_GND, F_Cu, priority=0)
zone(rect(0, 0, W, H), N_GND, B_Cu, priority=0)
# +5V pours (front): top strip, left strip, vertical fuse-feed bus
zone(rect(0, 0, 82.2, 12.0), N_5V, F_Cu, priority=3)
zone(rect(0, 0, 20.2, 44.0), N_5V, F_Cu, priority=2)
zone(rect(70.0, 0, 82.2, 55.4), N_5V, F_Cu, priority=1, solid=True)

# ---------------- routing ----------------
# fuse outputs: join the two output clips, then straight into JST pin 1
for i in range(4):
    track([(89.2, JY[i]), (95.0, JY[i]), (101.0, JY[i])], N_5V_S[i], 2.0)

# R -> JST data pin (back layer, R is on the back)
for i in range(4):
    track([(99.11, JY[i] + 2.5), (101.0, JY[i] + 2.5)], N_DATA[i], 0.5, B_Cu)

# U1 VCC: straight from the left +5V strip along y=20 into pin 14
track([(19.5, 20.0), (38.38, 20.0)], N_5V, 1.0)
# C2 decoupling: +5V pad stub onto the VCC line, GND pad to a via
track([(32.05, 21.8), (32.05, 20.0)], N_5V, 0.6)
track([(33.95, 21.8), (35.3, 21.8)], N_GND, 0.6)
via(35.3, 21.8, N_GND)

# --- data inputs, front layer ---
PIN = {n: pi_pin_xy(n) for n in (12, 19, 33, 40)}
# D18: Pi pin12 (even/top row) -> U1 pin 2
track([PIN[12], (29.07, 29.0), (40.92, 29.0), (40.92, 27.62)], N_GPIO[0], 0.4)
# D10: Pi pin19 (odd/bottom row) -> dodge between pads -> U1 pin 5
track([PIN[19], (40.5, 39.6), (40.5, 33.0), (48.54, 33.0), (48.54, 27.62)],
      N_GPIO[2], 0.4)
# D13: Pi pin33 -> dodge right -> up along x=58.28 -> DIP interior -> pin 12
track([PIN[33], (58.28, 39.6), (58.28, 23.8), (43.46, 23.8), (43.46, 20.0)],
      N_GPIO[1], 0.4)
# D21: Pi pin40 (top row, rightmost) -> up x=64.63 -> over to pin 9 from above
track([PIN[40], (64.63, 17.2), (51.08, 17.2), (51.08, 20.0)], N_GPIO[3], 0.4)

# --- data outputs, back layer: U1 -> R (nested lanes, no crossings) ---
# ch1 (gate A, pin3) lane y13.4 -> R1
track([(43.46, 27.62), (42.2, 26.5), (42.2, 13.4), (95.8, 13.4),
       (97.29, JY[0] + 2.5)], N_D5V[0], 0.4, B_Cu)
# ch2 (gate D, pin11) lane y14.6, drop x93.1 -> R2
track([(46.0, 20.0), (47.27, 19.0), (47.27, 14.6), (93.1, 14.6),
       (93.1, JY[1] + 2.5), (97.29, JY[1] + 2.5)], N_D5V[1], 0.4, B_Cu)
# ch3 (gate B, pin6) lane y15.8, drop x92.1 -> R3
track([(51.08, 27.62), (52.35, 26.5), (52.35, 15.8), (92.1, 15.8),
       (92.1, JY[2] + 2.5), (97.29, JY[2] + 2.5)], N_D5V[2], 0.4, B_Cu)
# ch4 (gate C, pin8) lane y17.0, drop x91.1 -> R4
track([(53.62, 20.0), (54.9, 19.0), (54.9, 17.0), (91.1, 17.0),
       (91.1, JY[3] + 2.5), (97.29, JY[3] + 2.5)], N_D5V[3], 0.4, B_Cu)

# --- GND stitching vias ---
for (x, y) in [(3, 30), (16, 33), (3, 47), (25, 12.6), (35, 12.6), (50, 12.6),
               (62, 12.6), (68, 24), (68, 33), (87.5, 8), (95.5, 20), (95.5, 34),
               (95.5, 48), (105, 20), (105, 34), (105, 48), (105, 60), (75, 58),
               (40, 58), (20, 58), (55, 58), (87, 62)]:
    via(x, y, N_GND)

# ---------------- silkscreen ----------------
silk("gLED Controller", 33, 3.5, 2.0)
silk("5V 20A IN", 15.5, 18.7, 1.0)
silk("+", 13.0, 16.4, 1.5); silk("-", 18.08, 16.4, 1.5)
for i in range(4):
    silk(f"5A", 90.5, JY[i] - 4.3, 1.0)
labels = ["S1 GPIO18", "S2 GPIO13", "S3 GPIO10", "S4 GPIO21"]
for i in range(4):
    silk(labels[i], 91.5, JY[i] + 7.3, 1.0)
    silk("+", 96.5, JY[i], 1.0)
    silk("D", 96.5, JY[i] + 2.5, 1.0)
    silk("G", 96.5, JY[i] + 5.0, 1.0)
silk("Pi Zero 2 WH under board, pins up", 40.5, 51, 1.2, pcbnew.B_SilkS)
silk("74AHCT125", 46, 31.5, 1.0)

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
board.Save("led-controller.kicad_pcb")
print("board written: led-controller.kicad_pcb ; U1 rot =", u1rot)
