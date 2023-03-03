from Foundation.System import System
from Notification import Notification

from StrategyGuideController.StrategyGuideControllerManager import StrategyGuideControllerManager


class SystemStrategyGuidePagesDisable(System):
    def __init__(self):
        super(SystemStrategyGuidePagesDisable, self).__init__()
        self.onLayerGroupPreparationObserver = None
        pass

    def _onRun(self):
        self.onLayerGroupPreparationObserver = Notification.addObserver(Notificator.onLayerGroupEnableBegin,
                                                                        self._onLayerGroupPreparation)
        return True
        pass

    def _onLayerGroupPreparation(self, groupName):
        if groupName == "StrategyGuide_Pages":
            self._disableContent()
            return False
            pass
        return False
        pass

    def _disableContent(self):
        pages = StrategyGuideControllerManager.getPages()

        for page in pages.values():
            page.setEnable(False)
            pass
        pass

    def _onStop(self):
        Notification.removeObserver(self.onLayerGroupPreparationObserver)
        self.onLayerGroupPreparationObserver = None
        pass

    pass
