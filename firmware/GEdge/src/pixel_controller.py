# NeoPixel strip control, decoupled from the HTTP server.

import time

import neopixel


class PixelController:
    def __init__(self, pin, num_pixels, order=neopixel.GRB, brightness=1.0):
        self.num_pixels = num_pixels
        self.pixels = neopixel.NeoPixel(
            pin,
            num_pixels,
            brightness=brightness,
            auto_write=False,
            pixel_order=order,
        )

    def set_pixels(self, data):
        """Apply colors from a "r,g,b|r,g,b|..." string."""
        t_start = time.monotonic()
        for i, color in enumerate(data.split("|")):
            if i >= self.num_pixels:
                break
            r, g, b = (int(c) for c in color.split(","))
            self.pixels[i] = (r, g, b)
        t_parsed = time.monotonic()
        self.pixels.show()
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
        self.pixels.fill(color)

    def set_pixel(self, i, color):
        """Set a single pixel without showing."""
        self.pixels[i] = color

    def show(self):
        self.pixels.show()

    def set_brightness(self, value):
        """Set strip brightness. NeoPixel expects a float in 0.0 - 1.0."""
        self.pixels.brightness = max(0.0, min(1.0, value))
        self.pixels.show()

    def clear(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
