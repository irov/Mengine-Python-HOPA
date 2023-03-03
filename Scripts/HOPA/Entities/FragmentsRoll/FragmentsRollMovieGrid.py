class FragmentsRollMovieSlot(object):
    def __init__(self, x, y, node):
        self.x = x
        self.y = y
        self.node = node


class FragmentsRollMovieGrid(object):
    def __init__(self, grid, movieObj, cells):
        self.movie = movieObj.getEntity()
        self.slots = []
        self.grid = grid

        self.collectSlots(cells)
        pass

    def finalize(self):
        self.movie = None

        self.clear()
        self.slots = []

        self.grid = None
        pass

    def getSlot(self, x, y):
        for slot in self.slots:
            if slot.x != x or slot.y != y:
                continue
                pass
            return slot.node
            pass

        return None
        pass

    def setNode(self, x, y, node):
        slot = self.getSlot(x, y)

        slot.addChild(node.node)
        pass

    def collectSlots(self, cells):
        for cell in cells:
            MovieSlotName = cell['MovieSlotName']
            slotNode = self.movie.getMovieSlot(MovieSlotName)
            slot = FragmentsRollMovieSlot(cell["X"], cell["Y"], slotNode)
            self.slots.append(slot)
            pass
        pass

    def clear(self):
        for slot in self.slots:
            slot.node.removeChildren()
            pass
        pass

    def refresh(self):
        def visitor(element):
            x = element.getX()
            y = element.getY()
            slot = self.getSlot(x, y)
            node = element.getNode()
            node.removeFromParent()
            slot.addChild(node)
            pass

        self.clear()
        self.grid.visitElements(visitor)
        pass
