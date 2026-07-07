class Container():
    def __init__(self):
        self._children = []
        self.x = 0
        self.y = 0

    def addChild(self, child):
        self._children.append(child)

    def addChildAt(self, child, index):
        self._children.insert(index, child)

    def removeChild(self, child):
        self._children.remove(child)

    def removeChildren(self):
        self._children = []

    def getWidth(self):
        return max([child.x + child.width for child in self._children])

    def getHeight(self):
        return max([child.y + child.height for child in self._children])

    def get_pixels(self):
        pixel_dict = {}
        for child in self._children:
            for (x, y, color) in child.get_pixels():
                pixel_dict[(x + self.x, y + self.y)] = color

        return [(x, y, color) for (x, y), color in pixel_dict.items()]