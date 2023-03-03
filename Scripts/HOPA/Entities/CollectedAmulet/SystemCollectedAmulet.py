from Foundation.DemonManager import DemonManager
from Foundation.System import System


class SystemCollectedAmulet(System):

    def _onRun(self):
        self.addObserver(Notificator.onCollectedAmuletAdd, self.__onCollectedAmuletAdd)

    def __onCollectedAmuletAdd(self):
        Amulet = DemonManager.getDemon("CollectedAmulet")
        oldValue = Amulet.getCurrentCount()
        new = oldValue + 1
        Amulet.setCurrentCount(new)
        return False
