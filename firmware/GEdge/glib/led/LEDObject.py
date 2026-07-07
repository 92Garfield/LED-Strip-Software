class LEDObject():
    def __init__(self, pixels):
        if (type(pixels) == list):
            self._pixels = pixels
            self._dict = {}
            for (x, y) in pixels:
                self._dict[(x, y)] = (0, 0, 0)
        elif (type(pixels) == dict):
            self._dict = pixels
            self._pixels = [(x, y) for (x, y) in self._dict.keys()]
        else:
            raise ValueError("pixels must be a list or dict")

        self.x = 0
        self.y = 0

    def fill(self, color):
        for pos in self._dict:
            self._dict[pos] = color

    def set_pixel(self, pos, color):
        if (type(pos) == tuple):
            if (pos in self._dict):
                self._dict[pos] = color
            else:
                raise ValueError("Position not in object")
        elif (type(pos) == int):
            if (pos < len(self._pixels) and pos >= 0):
                self._dict[self._pixels[pos]] = color
            else:
                raise ValueError("Position out of range")

    def get_pixel_count(self):
        return len(self._pixels)

    def get_pixels(self):
        return [(x + self.x, y + self.y, color) for (x, y), color in self._dict.items()]

    @property
    def width(self):
        if len(self._pixels) == 0:
            return 1

        return max([x for (x, y) in self._pixels]) + 1

    @property
    def height(self):
        if len(self._pixels) == 0:
            return 1

        return max([y for (x, y) in self._pixels]) + 1