# Configuration for the 4-strip GEdge Zero controller.
#
# Copy this file to config.py and adjust for your hardware. config.py is
# gitignored (it's local to one Pi) - see README.md for setup.

# HTTP server bind address/port. Port 80 needs root, but rpi_ws281x needs
# root anyway (DMA/PWM access), so this project is normally run with sudo.
HOST = "0.0.0.0"
PORT = 80

# One entry per JST connector on the "4-strips, 4-power" PCB - see
# "PCB/simplified/4-strips, 4-power/pcb.md" for the GPIO <-> connector table.
# gpio/channel/dma identify the physical output; the rest is metadata
# exposed to clients (same idea as GEdge's LED_NAME/LENGTH_CM/PHYSICAL).
STRIPS = {
    "S1": dict(
        gpio=18, channel=0, dma=10,  # J2, PWM0
        num_pixels=150,
        name="GEdge Zero S1",
        length_cm=500.0,
        physical=[(0, 0), (500, 0)],
    ),
    "S2": dict(
        gpio=13, channel=1, dma=11,  # J4, PWM1
        num_pixels=150,
        name="GEdge Zero S2",
        length_cm=500.0,
        physical=[(0, 0), (500, 0)],
    ),
    "S3": dict(
        gpio=10, channel=0, dma=12,  # J5, SPI0
        num_pixels=150,
        name="GEdge Zero S3",
        length_cm=500.0,
        physical=[(0, 0), (500, 0)],
    ),
    "S4": dict(
        gpio=21, channel=0, dma=13,  # J3, PCM
        num_pixels=150,
        name="GEdge Zero S4",
        length_cm=500.0,
        physical=[(0, 0), (500, 0)],
    ),
}

# Animation started automatically after boot, per strip (module name in
# /animations). Set an entry to None to boot that strip idle.
DEFAULT_ANIMATIONS = {
    "S1": "rainbow_loop",
    "S2": "rainbow_loop",
    "S3": "rainbow_loop",
    "S4": "rainbow_loop",
}
