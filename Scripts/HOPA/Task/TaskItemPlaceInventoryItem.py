from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskItemPlaceInventoryItem(MixinItem, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskItemPlaceInventoryItem, self)._onParams(params)

        self.taken = params.get("Taken", True)
        self.pick = params.get("Pick", False)
        self.pickUp = params.get("PickUp", True)
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(TaskItemPlaceInventoryItem, self)._onInitialize()
        pass

    def _onRun(self):
        self.Item.setInteractive(True)

        if Mengine.hasTouchpad():
            # Chinese android touchpad hot fix
            self.addObserverFilter(Notificator.onInteractionClickEndUp, self._onItemFilter, self.Item)
        else:
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

        if self.taken is True:
            arrowItemEntity.take()
        else:
            if self.pick is False:
                arrowItemEntity.place()
                pass
            pass

        return True
        pass

    def _onFinally(self):
        super(TaskItemPlaceInventoryItem, self)._onFinally()

        self.Item.setInteractive(False)
        pass

    pass
