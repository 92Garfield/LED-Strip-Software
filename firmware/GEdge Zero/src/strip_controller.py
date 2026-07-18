# WS2812/NeoPixel strip control on Raspberry Pi GPIO, via rpi_ws281x.
#
# Mirrors the PixelController interface from
# firmware/GEdge/src/pixel_controller.py (the Pico W version) so
# animation_runner.py and the /animations modules are unchanged. One
# instance drives one physical strip on one GPIO/peripheral (PWM0, PWM1,
# PCM or SPI - see README.md for the pin table).

import time

from rpi_ws281x import PixelStrip, Color


class StripController:
    def __init__(self, gpio, num_pixels, channel=0, dma=10, freq_hz=800000,
                 invert=False, brightness=255):
        self.num_pixels = num_pixels
        self._strip = PixelStrip(
            num_pixels, gpio,
            freq_hz=freq_hz,
            dma=dma,
            invert=invert,
            brightness=brightness,
            channel=channel,
        )
        self._strip.begin()

    def set_pixels(self, data):
        """Apply colors from a "r,g,b|r,g,b|..." string."""
        t_start = time.monotonic()
        for i, color in enumerate(data.split("|")):
            if i >= self.num_pixels:
                break
            r, g, b = (int(c) for c in color.split(","))
            self._strip.setPixelColor(i, Color(r, g, b))
        t_parsed = time.monotonic()
        self._strip.show()
        t_shown = time.monotonic()
        print(
            "set_pixels: parse={:.1f}ms show={:.1f}ms total={:.1f}ms".format(
                (t_parsed - t_start) * 1000,
                (t_shown - t_parsed) * 1000,
                (t_shown - t_start) * 1000,
            )
        )

    def fill(self, color):
        """Set all pixels to one color without showing."""
        r, g, b = color
        packed = Color(r, g, b)
        for i in range(self.num_pixels):
            self._strip.setPixelColor(i, packed)

    def set_pixel(self, i, color):
        """Set a single pixel without showing."""
        r, g, b = color
        self._strip.setPixelColor(i, Color(r, g, b))

    def show(self):
        self._strip.show()

    def set_brightness(self, value):
        """Set strip brightness. Takes a float 0.0-1.0 (same contract as
        GEdge's PixelController); rpi_ws281x itself wants 0-255.
        """
        self._strip.setBrightness(int(max(0.0, min(1.0, value)) * 255))
        self._strip.show()

    def clear(self):
        self.fill((0, 0, 0))
        self.show()
