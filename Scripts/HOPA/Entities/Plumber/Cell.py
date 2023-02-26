class Cell(object):
    def __init__(self, position, width, height, movie, data):
        self.width = width
        self.height = height
        self.position = position
        self.movie = movie
        self.data = data
        pass

    def getWidth(self):
        return self.width
        pass

    def getHeight(self):
        return self.height
        pass

    def getPosition(self):
        return self.position
        pass

    def getMovie(self):
        return self.movie
        pass

    def getData(self):
        return self.data
        pass

    def setData(self, newData):
        self.data = newData
        pass

    def onDestroy(self):
        if self.movie is not None:
            movieEntity = self.movie.getEntity()
            movieEntity.removeFromParent()
            self.movie.removeFromParent()
            self.movie = None
            pass

        self.width = None
        self.height = None
        self.position = None
        self.movie = None
        self.data = None
        pass
    pass