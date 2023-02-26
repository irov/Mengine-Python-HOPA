class Slot(object):
    def __init__(self):
        pass
        self._isWait = True
        self._previousSlot = None
        self._socket = None
        self._slot = None
        self._movie = None
        self.orientation = ""
        self.orientationInput = ""
        self.orientationOutput = ""
        self._enigmaObject = None

        self.movieID = {'EE': 'EW', 'WW': 'EW', 'NN': 'NS', 'SS': 'NS', 'E': 'E', 'S': 'S', 'SE': 'SW', 'N': 'N', 'NE': 'NW', 'ES': 'EN', 'W': 'W', 'SW': 'ES', 'EN': 'ES', 'WN': 'SW', 'WS': 'NW', 'NW': 'EN'}
    def setPrevious(self, slot):
        self._previousSlot = slot
        pass

    def getPrevious(self):
        return self._previousSlot
        pass

    def getOrientation(self):
        return self.orientation
        pass

    def setOrientation(self, value):
        self.orientation = value
        pass

    def getOrientationIn(self):
        return self.orientationInput
        pass

    def setOrientationIn(self, value):
        self.orientationInput = value
        pass

    def getOrientationOut(self):
        return self.orientationOutput
        pass

    def setOrientationOut(self, value):
        self.orientationOutput = value
        pass

    def getMovie(self):
        return self._movie
        pass

    def setMovie(self, movie):
        self._movie = movie
        pass

    def setSocket(self, socket):
        self._socket = socket
        pass

    def getSocket(self):
        return self._socket
        pass

    def getSlot(self):
        return self._slot
        pass

    def setSlot(self, slot):
        self._slot = slot
        pass

    def destroy(self):
        self.destroyOwn()
        if self._previousSlot is not None:
            self._previousSlot.destroy()
            self._previousSlot = None
            pass
        pass

    def destroyOwn(self):
        if self._movie is not None:
            self._movie.removeFromParent()
            self._movie = None
            pass
        pass

    def updateMovie(self):
        self.destroyOwn()
        self.orientation = self.orientationInput + self.orientationOutput
        self.recoverMovie()
        pass

    def recoverMovie(self):
        if self._previousSlot is not None:
            slotName = self._slot.getName()
            movieName = "%s_%s" % (str(slotName), str(self.orientation))
            self._movie = self._enigmaObject.generateObject(movieName, "Movie_Slot_%s" % self.movieID[self.orientation])
            movieEntityNode = self._movie.getEntityNode()
            self._slot.addChild(movieEntityNode)
            pass
        pass

    def getPathSlotOrientation(self):
        PathSlotOrientation = []
        slotName = self._slot.getName()
        PathSlotOrientation.append((str(slotName), self.orientation))
        if self._previousSlot is not None:
            PathSlotOrientation = PathSlotOrientation + self._previousSlot.getPathSlotOrientation()
            pass
        return PathSlotOrientation
        pass
    pass