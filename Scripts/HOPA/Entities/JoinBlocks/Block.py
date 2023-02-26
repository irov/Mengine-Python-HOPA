class Block(object):
    def __init__(self):
        self._slot = None
        self._state = None
        self._movieWait = None
        self._movieActive = None
        self._name = None
        self._socket = None
        self._blocked = False
        self._slotName = None
        pass

    def getName(self):
        return self._name
        pass

    def setName(self, name):
        self._name = name
        pass

    def getSocket(self):
        return self._socket
        pass

    def setSocket(self, socket):
        self._socket = socket
        self._socket.setPosition((0, 0))
        self._socket.setInteractive(True)
        _socketEntityNode = self._socket.getEntityNode()
        self._slot.addChild(_socketEntityNode)
        pass

    def getMovieWait(self):
        return self._movieWait
        pass

    def setMovieWait(self, movie):
        self._movieWait = movie
        pass

    def getMovieActive(self):
        return self._movieActive
        pass

    def setMovieActive(self, movie):
        self._movieActive = movie
        pass

    def getSlot(self):
        return self._slot
        pass

    def setSlot(self, slot):
        self._slot = slot
        pass

    def getSlotName(self):
        return self._slotName
        pass

    def setSlotName(self, slotName):
        self._slotName = slotName
        pass
    def getState(self):
        return self._state
        pass

    def setState(self, state):
        movieActiveEntity = self._movieActive.getEntity()
        movieActiveEntityNode = self._movieActive.getEntityNode()

        movieWaitEntity = self._movieWait.getEntity()
        movieWaitEntityNode = self._movieWait.getEntityNode()

        if state is False:
            movieActiveEntity.removeFromParent()

            self._movieWait.setEnable(True)
            self._movieActive.setEnable(False)

            self._slot.addChild(movieWaitEntityNode)
            pass

        else:
            movieWaitEntity.removeFromParent()

            self._movieActive.setEnable(True)
            self._movieWait.setEnable(False)
            self._slot.addChild(movieActiveEntityNode)
            pass

        self._state = state
        pass

    def changeState(self):
        self.setState(not self._state)
        pass

    def destroy(self):
        if self._state is True:
            movieEntity = self._movieActive.getEntity()
            self._movieActive = None
            pass
        else:
            movieEntity = self._movieWait.getEntity()
            self._movieWait = None
            pass

        movieEntity.removeFromParent()
        pass

    pass

pass