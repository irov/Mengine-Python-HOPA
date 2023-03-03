from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskItemPlaceInventoryAccumulateItem(MixinItem, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskItemPlaceInventoryAccumulateItem, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        self.Value = params.get("Value")
        pass

    def _onInitialize(self):
        super(TaskItemPlaceInventoryAccumulateItem, self)._onInitialize()
        pass

    def _onRun(self):
        self.Item.setInteractive(True)

        self.addObserverFilter(Notificator.onItemClick, self._onItemFilter, self.Item)

        return False
        pass

    def _onItemFilter(self, item):
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False
            pass

        if self.InventoryItem is not attach:
            return False
            pass

        arrowItemEntity = self.InventoryItem.getEntity()
        if self.InventoryItem.reduceValue(self.Value) == "back":
            arrowItemEntity.pickAfterPlace()
            pass
        elif self.InventoryItem.reduceValue(self.Value) == "take":
            arrowItemEntity.take()
            pass
        else:
            arrowItemEntity.invalidUse()
            return False
            pass

        return True
        pass

    def _onFinally(self):
        super(TaskItemPlaceInventoryAccumulateItem, self)._onFinally()

        self.Item.setInteractive(False)
        pass

    pass
