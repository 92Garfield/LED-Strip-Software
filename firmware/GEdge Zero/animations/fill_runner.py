# Starts full blue. A single red pixel runs from the right edge to the left
# and stays there; the next runner stops one pixel earlier, and so on until
# the strip is fully red. Then the colors swap and blue fills back the same way.
#
# Identical to firmware/GEdge/animations/fill_runner.py.
#
# "Right" is LED index 0 - the first point of config's per-strip `physical`.
# The runner travels toward index num-1, where the stack grows.


class Animation:
    """move_interval: seconds between runner moves
    base_color: fill color the runners travel over
    run_color: color of the runner (and of the growing stack)
    """

    def __init__(
        self,
        pixels,
        move_interval=0.02,
        base_color=(0, 0, 255),
        run_color=(255, 0, 0),
    ):
        self.pixels = pixels
        self.move_interval = move_interval
        self.base_color = base_color
        self.run_color = run_color
        self.num = pixels.num_pixels
        self.boundary = self.num  # stack occupies [boundary, num)
        self.pos = 0  # current runner position
        self.next_move = 0.0

    def start(self, now):
        self.pixels.fill(self.base_color)
        self.pixels.set_pixel(self.pos, self.run_color)
        self.pixels.show()
        self.next_move = now + self.move_interval

    def step(self, now):
        if now < self.next_move:
            return
        self.next_move = now + self.move_interval

        if self.pos < self.boundary - 1:
            # Advance the runner one pixel toward the stack.
            self.pixels.set_pixel(self.pos, self.base_color)
            self.pos += 1
            self.pixels.set_pixel(self.pos, self.run_color)
        else:
            # Runner reached the stack and stays; the next one starts right.
            self.boundary -= 1
            if self.boundary <= 0:
                # Strip is fully run_color: run back with the colors swapped.
                self.base_color, self.run_color = self.run_color, self.base_color
                self.boundary = self.num
            self.pos = 0
            self.pixels.set_pixel(self.pos, self.run_color)
        self.pixels.show()
