# LED Controller PCB

Carrier board for a Raspberry Pi Zero 2 W(H): takes 5 V from a power supply,
powers the Pi, level-shifts the data signals to 5 V and feeds up to four
WS2812-style strips through pluggable, individually fused connectors.

## Schematic (simplified)

### Power

```
                     C1
J1 +5V ────●────────1000µF───┐
           │                (GND)
           ├──────────────────────────► Pi 5V      (header pins 2 & 4)
           ├──[ F1 5A ]───────────────► J2 pin 1   +5V strip 1
           ├──[ F2 5A ]───────────────► J3 pin 1   +5V strip 2
           ├──[ F3 5A ]───────────────► J4 pin 1   +5V strip 3
           └──[ F4 5A ]───────────────► J5 pin 1   +5V strip 4

J1 GND ── ground plane ── Pi GND ── U1 GND ── J2..J5 pin 3
```

Mind the polarity at J1 — a reversed supply kills the Pi. Mark +/− clearly
on the silkscreen.

### Data (one of four identical channels)

```
Pi GPIO18 ────► U1 input      U1 output ───[ R1 470Ω ]───► J2 pin 2  DATA
(3.3 V logic)   └─ 74AHCT125, VCC = 5 V ─┘    (5 V logic)
                   + C2 100nF at VCC pin
```

Channel mapping: GPIO18 → J2, GPIO13 → J3, GPIO10 → J4, GPIO21 → J5.
(`rpi_ws281x` drives GPIO18/GPIO13 as PWM0/PWM1 simultaneously; GPIO10 = SPI
and GPIO21 = PCM are alternative single-channel outputs.)

## Parts

| Ref | Part | Why | JLCPCB |
|---|---|---|---|
| J1 | Screw terminal 5.08 mm 2P (KF301-5.0-2P) | 5 V power input, takes thick wire for high current | [C474881](https://jlcpcb.com/parts/componentSearch?searchTxt=C474881) |
| J2–J5 | JST XH 3-pin header (B3B-XH-A) | Pluggable strip outputs (+5V / DATA / GND) | [C144394](https://jlcpcb.com/parts/componentSearch?searchTxt=C144394) |
| J6 | Female header 2×20, 2.54 mm | Socket the Pi Zero 2 WH plugs into | [C2977589](https://jlcpcb.com/parts/componentSearch?searchTxt=C2977589) |
| U1 | SN74AHCT125N (DIP-14) | Shifts 3.3 V GPIO data to 5 V, one buffer per strip | [C354152](https://jlcpcb.com/parts/componentSearch?searchTxt=C354152) |
| R1–R4 | 470 Ω, 0805 | Protects first LED, damps ringing on the data line | [C17710](https://jlcpcb.com/parts/componentSearch?searchTxt=C17710) |
| C1 | 1000 µF 16 V electrolytic | Bulk capacitor: absorbs inrush and load spikes | [C43832](https://jlcpcb.com/parts/componentSearch?searchTxt=C43832) |
| C2 | 100 nF, 0805 | Decoupling for U1 | [C49678](https://jlcpcb.com/parts/componentSearch?searchTxt=C49678) |
| F1–F4 | 5×20 mm fuse clips (2 per fuse) + 5 A glass fuse | Per-strip overcurrent protection | [C3130](https://jlcpcb.com/parts/componentSearch?searchTxt=C3130) |

## Layout notes

- **Copper:** order 2 oz. Route +5V and GND as wide pours, not traces
  (4 strips × 5 A worst case at the input). See the PCB-trace mode of the
  wire calculator for widths.
- **Mounting:** 4× M2.5 holes matching the Pi Zero footprint (standoffs — the
  2×20 header must not carry mechanical load), plus corner holes for the case.
- **C1** close to J1; one extra electrolytic per strip connector is cheap
  insurance if strips are long.
- **R1–R4** as close to their JST connectors as possible.
- **Fuse rating:** 5 A ≈ 80 LEDs at full white; adjust to your strips. Strips
  longer than ~1–2 m should get power injected at the far end through their
  own wiring, not through the data pigtail.
- **Connector note:** most strips ship with JST **SM** pigtails (wire-to-wire).
  Either crimp XH plugs onto the strip wires or buy XH pigtails and solder
  them to the strips.
- U1 is the through-hole DIP variant for easy hand-soldering; if JLCPCB
  assembles the board, use the SOIC-14 version (SN74AHCT125DR) instead.
