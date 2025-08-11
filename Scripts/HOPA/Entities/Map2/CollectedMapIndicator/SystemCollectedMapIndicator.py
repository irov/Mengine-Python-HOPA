from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemCollectedMapIndicator(System):
    def __init__(self):
        super(SystemCollectedMapIndicator, self).__init__()
        self.onCollectedMapAddObserver = None
        pass

    def _onRun(self):
        self.onCollectedMapAddObserver = Notification.addObserver(Notificator.onCollectedMapAddPart, self.__onCollectedMapAdd)
        pass

    def _onStop(self):
        Notification.removeObserver(self.onCollectedMapAddObserver)
        pass

    def __onCollectedMapAdd(self, partId):
        Indicator = DemonManager.getDemon("CollectedMapIndicator")
        oldValue = Indicator.getCurrentValue()
        new = oldValue + 1
        Indicator.setCurrentValue(new)
        return False
        pass

    pass
