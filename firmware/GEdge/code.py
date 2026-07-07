# Entry point: WLAN-controlled NeoPixel LED strip on a Raspberry Pi Pico W.
# Application code lives in /src.

import sys
import time

import board

sys.path.append("/src")

import config
from status_light import StatusLight
from wifi_manager import connect
from pixel_controller import PixelController
from animation_runner import AnimationRunner
from led_server import create_server

time.sleep(1)

# Debug-by-light: off now, blinks while connecting, steady once connected.
status = StatusLight(
    connecting_interval=config.CONNECTING_BLINK_INTERVAL,
    pulse_interval=config.PULSE_BLINK_INTERVAL,
    pulse_count=config.PULSE_COUNT,
)
status.off()

# Connect to WiFi (station mode, static IP) and get a socket pool.
pool = connect(
    config.WIFI_SSID,
    config.WIFI_PASSWORD,
    config.STATIC_IP,
    config.NETMASK,
    config.GATEWAY,
    config.TX_POWER,
    status=status,
)
status.connected()

# Set up the LED strip and the animation runner.
pixels = PixelController(board.GP0, config.NUM_PIXELS)
runner = AnimationRunner(pixels)

# Build and start the HTTP server.
server = create_server(pool, pixels, runner, status=status)
server.start(config.STATIC_IP)
print("Server started at", config.STATIC_IP)

# Animate without a client until someone connects.
if config.DEFAULT_ANIMATION:
    runner.run_animation(config.DEFAULT_ANIMATION)
    print("Running animation:", config.DEFAULT_ANIMATION)

# Main loop: poll the server, advance the animation, drive the status LED.
while True:
    try:
        server.poll()
        runner.update()
        status.update()
    except Exception:  # pylint: disable=broad-except
        continue
