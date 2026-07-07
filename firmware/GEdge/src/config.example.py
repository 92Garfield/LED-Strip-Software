# Configuration for the WLAN-controlled LED strip.

# Copy this file to config.py and fill in local WiFi credentials.
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Static network configuration
STATIC_IP = "192.168.2.42"
NETMASK = "255.255.255.0"
GATEWAY = "192.168.2.1"
TX_POWER = 15

# NeoPixel strip
NUM_PIXELS = 150

# Strip metadata, exposed to clients as the global gLED object on "/"
LED_NAME = "GEdge kueche"
LENGTH_CM = 500.0
# Physical layout of the strip as a polyline, (x, y) in cm.
PHYSICAL = [
    (330, 0),
    (330, 85),
    (12, 85),
    (12, 63),
    (0, 63),
    (0, 0),
]

# Animation started automatically after boot (module name in /animations).
# Set to None to boot with the strip idle.
DEFAULT_ANIMATION = "rainbow_loop"

# Status LED (debug-by-light), seconds
CONNECTING_BLINK_INTERVAL = 0.1
PULSE_BLINK_INTERVAL = 0.06
PULSE_COUNT = 5
