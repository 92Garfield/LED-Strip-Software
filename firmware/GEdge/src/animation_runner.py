# Runs animations from /animations as a non-blocking step loop, so the
# HTTP server stays responsive while the strip animates on its own.
#
# Every module in /animations defines a class named Animation with:
#   __init__(pixels, **params)  - pixels is the PixelController
#   start(now)                  - draw the first frame
#   step(now)                   - advance if the next frame is due

import time


def load_animation(name):
    """Import /animations/<name>.py and return its Animation class."""
    module = __import__("animations." + name, None, None, ("Animation",))
    return module.Animation


class AnimationRunner:
    def __init__(self, pixels):
        self.pixels = pixels
        self.current = None
        self.name = None

    def run_animation(self, name, **params):
        """Start the named animation, replacing any running one."""
        cls = load_animation(name)
        animation = cls(self.pixels, **params)
        animation.start(time.monotonic())
        self.current = animation
        self.name = name

    def stop(self):
        self.current = None
        self.name = None

    def update(self):
        """Advance the running animation; call this from the main loop."""
        if self.current is not None:
            self.current.step(time.monotonic())
