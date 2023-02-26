from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskInventoryCombineInventoryItem(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskInventoryCombineInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")

        self.AttachInventoryItem = params.get("AttachInventoryItem")
        self.SlotInventoryItem = params.get("SlotInventoryItem")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onInventoryCombineInventoryItem, self._combineInventoryItemFilter, self.Inventory)

        return False
        pass

    def _actionEnergy(self):
        if SystemManager.hasSystem("SystemEnergy") is False:
            return True

        SystemEnergy = SystemManager.getSystem("SystemEnergy")

        if SystemEnergy.performAction("CombineItems") is True:
            # if 'CombineItems' not enabled or this mechanic is disabled it also return True
            return True
        return False

    def _combineInventoryItemFilter(self, Inventory, AttachInventoryItem, SlotInventoryItem):
        if self.AttachInventoryItem != AttachInventoryItem:
            return False
            pass

        if self.SlotInventoryItem != SlotInventoryItem:
            return False
            pass

        if self._actionEnergy() is False:
            return False

        AttachInventoryItem = self.AttachInventoryItem

        AttachInventoryItemEntity = AttachInventoryItem.getEntity()
        AttachInventoryItemEntity.combine()

        return True
        pass
    pass