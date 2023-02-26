from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Notification import Notification

class SystemCollectedAmulet(System):

    def __init__(self):
        super(SystemCollectedAmulet, self).__init__()
        self.onCollectedAmuletAddObserver = None
        pass

    def _onRun(self):
        self.onCollectedAmuletAddObserver = Notification.addObserver(Notificator.onCollectedAmuletAdd, self.__onCollectedAmuletAdd)
        pass

    def _onStop(self):
        Notification.removeObserver(self.onCollectedAmuletAddObserver)
        pass

    def __onCollectedAmuletAdd(self):
        Amulet = DemonManager.getDemon("CollectedAmulet")
        oldValue = Amulet.getCurrentCount()
        new = oldValue + 1
        Amulet.setCurrentCount(new)
        return False
        pass
    pass