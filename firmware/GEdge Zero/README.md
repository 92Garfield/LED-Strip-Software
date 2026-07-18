# GEdge Zero

HTTP-controlled WS2812/NeoPixel firmware for a **Raspberry Pi Zero family**
board (Zero W, Zero WH, Zero 2 W), driving up to **4 independent LED
strips** from the ["4-strips, 4-power" PCB](<../../PCB/simplified/4-strips, 4-power/pcb.md>).

This is the Pi Zero counterpart to [`../GEdge`](<../GEdge>) (which runs on a
Pico W under CircuitPython): same architecture (`src/` app code,
`animations/` step-based effects, `glib/` color helpers), but written in
regular Python 3 for Raspberry Pi OS, since the Pi Zero runs full Linux
rather than a microcontroller RTOS.

## Hardware

| Connector | GPIO (BCM) | Header pin | Peripheral | Firmware strip |
|---|---|---|---|---|
| J2 | GPIO18 | 12 | PWM0  | S1 |
| J4 | GPIO13 | 33 | PWM1  | S2 |
| J5 | GPIO10 | 19 | SPI0  | S3 |
| J3 | GPIO21 | 40 | PCM   | S4 |

These four GPIOs were chosen because each is driven by a **different**
hardware peripheral capable of generating the WS2812 timing via DMA
(2x PWM, PCM, SPI) - so all four strips can run simultaneously without one
blocking another. See the PCB's `pcb.md` for the full board writeup, and
`J7-J10` for the power-only injection connectors on long strips.

## 1. Flash and boot Raspberry Pi OS

Use **Raspberry Pi OS Lite** (headless, no desktop) via Raspberry Pi
Imager. In the imager's settings (gear icon) before writing:
- Enable SSH
- Set your WiFi SSID/password
- Set a hostname/username/password

Boot the Pi and confirm you can SSH in:
```
ssh <username>@<hostname>.local
```

## 2. Enable SPI and free up the PCM/audio peripheral

Strip S3 (GPIO10) needs SPI enabled, and strip S4 (GPIO21) needs the
onboard audio disabled (it uses the same PCM peripheral and will conflict
with the LED timing otherwise).

```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
```

Then edit `/boot/firmware/config.txt` (or `/boot/config.txt` on older OS
versions) and make sure audio is off:
```
dtparam=audio=off
```

Reboot after these changes: `sudo reboot`

## 3. Get the code onto the Pi

```bash
git clone <this repo's URL>
cd "LED-Strip-Software/firmware/GEdge Zero"
```

## 4. Install dependencies

`rpi_ws281x` needs root to access DMA/PWM, and building its C extension
needs a compiler - both are handled below.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv build-essential
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure your strips

```bash
cp src/config.example.py src/config.py
nano src/config.py
```
Adjust `num_pixels`, `name`, `length_cm` and `physical` per strip to match
your actual strips (the GPIO/channel/dma values already match the PCB
table above - only change those if you rewired something).

## 6. Run it

`rpi_ws281x` requires root:

```bash
sudo venv/bin/python3 main.py
```

You should see each strip initialize and start its `DEFAULT_ANIMATIONS`
entry (rainbow by default). Visit `http://<hostname>.local/` from a
browser to confirm the server is up. The page is compatible with the gLED
Chrome/Firefox client: the first configured strip is exposed as the global
`gLED` object (and shown in the page body), additional strips as `gLED2`,
`gLED3`, `gLED4`; each object carries its `strip` value for the `/data`
field below.

### Control API

`POST /data` (form-encoded), same contract as GEdge, plus a `strip` field:

| Field | Values | Notes |
|---|---|---|
| `strip` | `S1`, `S2`, `S3`, `S4`, `all` | Which output to target. Defaults to `S1`. Ignored for `shutdown`. |
| `type` | `set`, `brightness`, `animation`, `shutdown` | `shutdown` powers off the Pi (safe to unplug once its LED stops blinking). |
| `data` | `"r,g,b\|r,g,b\|..."` (set) / `0-100` (brightness) / animation name or `stop` (animation) | Ignored for `shutdown`. |

## 7. Run automatically on boot (systemd)

Create `/etc/systemd/system/gedge-zero.service`:
```ini
[Unit]
Description=GEdge Zero LED controller
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/<username>/LED-Strip-Software/firmware/GEdge Zero
ExecStart="/home/<username>/LED-Strip-Software/firmware/GEdge Zero/venv/bin/python3" main.py
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gedge-zero.service
sudo journalctl -u gedge-zero -f   # follow logs
```

## Troubleshooting

- **`ws2811_init failed`**: another process is already using that DMA
  channel/peripheral, or SPI/audio wasn't configured per step 2. Check
  `dmesg` and confirm `dtparam=audio=off` and SPI is enabled.
- **Flicker / glitches on GPIO10 or GPIO21**: these carry 3.3 V logic
  straight into nominally-5 V strips (no level shifter on the simplified
  PCB) - keep data leads short, as noted in the PCB's `pcb.md`.
- **Strips don't turn off when you stop the script**: use `Ctrl+C` (SIGINT)
  or `systemctl stop`, not `kill -9` - the signal handler in `main.py`
  clears all strips on exit; `SIGKILL` skips it.
