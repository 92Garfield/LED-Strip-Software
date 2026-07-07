# Whole strip in a single color whose hue rotates through all HUE values.

from glib.color import hsv_to_rgb


class Animation:
    """interval: seconds between color changes
    hue_step: degrees the hue advances per change
    """

    def __init__(self, pixels, interval=0.1, hue_step=2.0):
        self.pixels = pixels
        self.interval = interval
        self.hue_step = hue_step
        self.hue = 0.0
        self.next_change = 0.0

    def start(self, now):
        self.next_change = now
        self.step(now)

    def step(self, now):
        if now < self.next_change:
            return
        self.next_change = now + self.interval
        self.pixels.fill(hsv_to_rgb(self.hue))
        self.pixels.show()
        self.hue = (self.hue + self.hue_step) % 360.0
