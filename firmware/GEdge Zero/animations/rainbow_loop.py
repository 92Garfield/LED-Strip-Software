# The whole strip shows one continuous rainbow: hues are spaced equally so
# the cycle closes on itself (the hue gap between the last and first pixel
# equals the gap between neighbors). The rainbow then rotates along the
# strip, wrapping around, at a configurable speed.
#
# Identical to firmware/GEdge/animations/rainbow_loop.py.

from glib.color import hsv_to_rgb


class Animation:
    """interval: seconds between redraws
    speed: hue degrees the rainbow moves per second (negative reverses)
    """

    def __init__(self, pixels, interval=0.05, speed=60.0):
        self.pixels = pixels
        self.interval = interval
        self.speed = speed
        self.num = pixels.num_pixels
        self.hue_spacing = 360.0 / self.num
        self.offset = 0.0
        self.last_draw = 0.0
        self.next_change = 0.0

    def _draw(self):
        for i in range(self.num):
            self.pixels.set_pixel(i, hsv_to_rgb(self.offset + i * self.hue_spacing))
        self.pixels.show()

    def start(self, now):
        self.last_draw = now
        self.next_change = now
        self.step(now)

    def step(self, now):
        if now < self.next_change:
            return
        self.next_change = now + self.interval
        self.offset = (self.offset + self.speed * (now - self.last_draw)) % 360.0
        self.last_draw = now
        self._draw()
