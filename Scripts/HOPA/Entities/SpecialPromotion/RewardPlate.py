from Foundation.DemonManager import DemonManager
from Foundation.Utils import getCurrentPublisher
from Foundation.MonetizationManager import MonetizationManager


class RewardPlate(object):

    def __init__(self, movie):
        self.movie = movie
        self.icons = []

    def createIcons(self):
        game_store_name = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")
        current_publisher = getCurrentPublisher()
        GameStore = DemonManager.getDemon(game_store_name)

        def _createIcon(slot_name, object_name):
            slot = self.movie.getMovieSlot(slot_name)
            icon = GameStore.generateIcon(object_name, "{}_{}".format(object_name, current_publisher), Enable=True)
            slot.addChild(icon.getEntityNode())
            self.icons.append(icon)

        _createIcon("gold", "Movie2_Coin")
        _createIcon("energy", "Movie2_Energy")

    def getEntityNode(self):
        return self.movie.getEntityNode()

    def setEnable(self, state):
        self.movie.setEnable(bool(state))

    def cleanUp(self):
        to_destroy = self.icons + [self.movie]

        for movie in to_destroy:
            movie.removeFromParent()
            movie.onDestroy()

        self.icons = None
        self.movie = None
