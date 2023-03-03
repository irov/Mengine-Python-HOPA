from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.Task import Task


class TaskInventoryDetachItem(MixinInventoryItem, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventoryDetachItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        pass

    def _onCheck(self):
        if self.Inventory.isActive() is False:
            return False
            pass

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()

        if InventoryEntity.isActivate() is False:
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.Inventory.detachItem(self.InventoryItem)

        return True
        pass

    pass
