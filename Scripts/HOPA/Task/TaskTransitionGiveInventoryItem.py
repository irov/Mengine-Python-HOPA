from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskTransitionGiveInventoryItem(MixinTransition, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskTransitionGiveInventoryItem, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", False)
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Transition.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onTransitionUse, self._onTransitionClickFilter, self.Transition)

        return False
        pass

    def _onFinally(self):
        super(TaskTransitionGiveInventoryItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Transition.setInteractive(False)
            pass
        pass

    def _onTransitionClickFilter(self, Transition):
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False
            pass

        if self.InventoryItem is not attach:
            attachEntity = attach.getEntity()
            attachEntity.invalidUse(Transition)
            return False
            pass

        arrowItemEntity = self.InventoryItem.getEntity()

        arrowItemEntity.take()

        return True
        pass
    pass