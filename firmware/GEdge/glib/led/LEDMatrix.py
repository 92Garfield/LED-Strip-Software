import neopixel

class LEDMatrix():
    def __init__(self, pin, width, height):
        self.width = width
        self.height = height
        self.matrix = [[(0, 0, 0) for x in range(width)] for y in range(height)]

        self.neopixel = neopixel.NeoPixel(pin, width * height, brightness=0.01, auto_write=False, pixel_order=neopixel.GRB)

    def get_pixel_index(self, x, y):
        # Matrix is created of S shaped strip
        if y % 2 == 0:
            return y * self.width + x
        else:
            return ((y + 1) * self.width) - x - 1

    def set_pixel(self, x, y, color):
        self.matrix[y][x] = color
        self.neopixel[self.get_pixel_index(x, y)] = color

    def get_pixel(self, x, y):
        return self.matrix[y][x]

    def set_pixels(self, pixels):
        for (x, y, color) in pixels:
            self.set_pixel(x, y, color)

    def show(self):
        self.neopixel.show()

    def fill(self, color):
        self.neopixel.fill(color)
        for y in range(self.height):
            for x in range(self.width):
                self.matrix[y][x] = color