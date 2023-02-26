from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinZoom
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskZoomGiveInventoryItem(MixinZoom, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskZoomGiveInventoryItem, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", False)
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Zoom.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onZoomUse, self._onZoomClickFilter, self.Zoom)

        return False
        pass

    def _onFinally(self):
        super(TaskZoomGiveInventoryItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Zoom.setInteractive(False)
            pass
        pass

    def _onZoomClickFilter(self, zoom):
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False
            pass

        if self.InventoryItem is not attach:
            attachEntity = attach.getEntity()
            attachEntity.invalidUse(zoom)
            return False
            pass

        arrowItemEntity = self.InventoryItem.getEntity()

        arrowItemEntity.take()

        return True
        pass
    pass