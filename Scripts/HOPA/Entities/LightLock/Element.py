class Element(object):
    def __init__(self, enigmaObject, valueData):
        self.enigmaObject = enigmaObject
        self.value = None
        self.selectMovie = None
        self.currentMovie = None
        self.activateMovie = None
        self.valueData = valueData
        self.waitData = {}
        self.isWinPos = False
        pass

    def __repr__(self):
        return "Element ->%s %s %s" % (self.value, self.activateMovie.getName(), self.selectMovie.getName())
        pass

    def setWaitData(self, value):
        self.waitData = value
        pass

    def getIsWinPos(self):
        return self.isWinPos
        pass

    def setIsWinPos(self, value):
        self.isWinPos = value
        pass

    def setActivate(self, value):
        self.activateMovie.setEnable(value)
        self.activateMovie.setPlay(value)
        pass

    def UpdateActivateMovie(self, value):
        if self.activateMovie is None:
            return
            pass
        self.currentMovie.setEnable(not value)
        self.activateMovie.setEnable(value)
        pass

    def getValue(self):
        return self.value
        pass

    def setValue(self, value):
        self.value = value
        self.updateCurrentMovie()
        pass

    def updateCurrentMovie(self):
        if self.activateMovie is not None:
            self.activateMovie.setPlay(False)
            self.activateMovie.setEnable(False)
            pass
        activateMovieName = self.valueData[self.value]
        activateMovie = self.enigmaObject.getObject(activateMovieName)
        activateMovie.setLoop(True)
        self.activateMovie = activateMovie
        if self.currentMovie is not None:
            self.currentMovie.setPlay(False)
            self.currentMovie.setEnable(False)
            self.currentMovie = None
            pass
        movieName = self.waitData[self.value]
        movie = self.enigmaObject.getObject(movieName)
        movie.setEnable(True)
        movie.setLoop(True)
        movie.setPlay(True)
        self.currentMovie = movie
        pass

    def getCurrentMovie(self):
        return self.currentMovie
        pass

    def getSelectMovie(self):
        return self.selectMovie
        pass

    def setSelectMovie(self, movie):
        self.selectMovie = movie
        pass

    def onSelect(self):
        if self.selectMovie is None:
            return
            pass
        self.selectMovie.setEnable(True)
        self.selectMovie.setLoop(True)
        self.selectMovie.setPlay(True)
        pass

    def onDeselect(self):
        if self.selectMovie is None:
            return
            pass
        self.selectMovie.setPlay(False)
        self.selectMovie.setEnable(False)
        pass

    def onDestroy(self):
        entity = self.selectMovie.getEntity()
        entity.removeFromParent()
        self.selectMovie = None
        self.enigmaObject = None
        self.value = None
        self.selectMovie = None
        self.currentMovie = None
        self.valueData = None
        self.isWinPos = False
        self.activateMovie = None
        self.waitData = {}
        pass
    pass