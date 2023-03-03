class FragmentsRollElement(object):
    def __init__(self, type):
        super(FragmentsRollElement, self).__init__()
        self.x = None
        self.y = None
        self.node = None
        self.type = type
        pass

    def getType(self):
        return self.type
        pass

    def setCoord(self, x, y):
        self.setX(x)
        self.setY(y)
        pass

    def setX(self, x):
        self.x = x
        pass

    def setY(self, y):
        self.y = y
        pass

    def getX(self):
        return self.x
        pass

    def getY(self):
        return self.y
        pass

    def getNode(self):
        return self.node
        pass

    def finalize(self):
        self._onFinalise()
        pass

    pass
