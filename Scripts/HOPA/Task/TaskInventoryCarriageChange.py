from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskInventoryCarriageChange(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskInventoryCarriageChange, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onInventoryCurrentSlotIndex, self._onInventoryCurrentSlotIndex, self.Inventory)

        return False
        pass

    def _onInventoryCurrentSlotIndex(self, Inventory, Value):
        return True
        pass

    pass
