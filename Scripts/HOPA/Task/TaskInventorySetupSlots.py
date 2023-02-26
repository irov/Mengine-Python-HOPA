from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskInventorySetupSlots(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskInventorySetupSlots, self)._onParams(params)

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