class PurchaseButton(object):

    def __init__(self, movie):
        self.movie = movie

    def getEntityNode(self):
        return self.movie.getEntityNode()

    def setEnable(self, state):
        self.movie.setEnable(bool(state))

    def cleanUp(self):
        self.movie.removeFromParent()
        self.movie.onDestroy()
        self.movie = None
