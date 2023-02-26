from Foundation.System import System
from Notification import Notification

from StrategyGuideZoomManager import StrategyGuideZoomManager

class SystemStrategyGuideZoomsDisable(System):
    def __init__(self):
        super(SystemStrategyGuideZoomsDisable, self).__init__()
        self.onLayerGroupPreparationObserver = None
        pass

    def _onRun(self):
        self.onLayerGroupPreparationObserver = Notification.addObserver(Notificator.onLayerGroupEnableBegin, self._onLayerGroupPreparation)
        return True
        pass

    def _onLayerGroupPreparation(self, groupName):
        if groupName == "StrategyGuide_Zooms":
            self._disableZooms()
            return False
            pass
        return False
        pass

    def _disableZooms(self):
        zooms = StrategyGuideZoomManager.getZooms()

        for zooms in zooms.values():
            zooms.setEnable(False)
            pass
        pass

    def _onStop(self):
        Notification.removeObserver(self.onLayerGroupPreparationObserver)
        self.onLayerGroupPreparationObserver = None
        pass

    pass