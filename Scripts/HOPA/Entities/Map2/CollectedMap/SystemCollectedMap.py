from Foundation.System import System

from CollectedMapManager import CollectedMapManager

class SystemCollectedMap(System):
    def __init__(self):
        super(SystemCollectedMap, self).__init__()
        self.onCollectedMapAddObserver = None
        pass

    def _onRun(self):
        self.onCollectedMapAddObserver = Notification.addObserver(Notificator.onCollectedMapAddPart, self.__onCollectedMapAdd)
        pass

    def _onStop(self):
        Notification.removeObserver(self.onCollectedMapAddObserver)
        pass

    def __onCollectedMapAdd(self, partId):
        Object = CollectedMapManager.getObjectByPart(partId)
        Object.appendParam("OpenParts", partId)
        return False
        pass

    pass
