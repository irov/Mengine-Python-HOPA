from Foundation.DefaultManager import DefaultManager
from Foundation.System import System


class SystemInventoryItemSelection(System):
    def _onParams(self, params):
        super(SystemInventoryItemSelection, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onInventorySlotItemEnter, self._onSlotMouseEnterFilter)
        self.addObserver(Notificator.onInventorySlotItemLeave, self._onSlotMouseLeaveFilter)
        pass

    def _onStop(self):
        pass

    def __getSlot(self, slotId):
        InventoryEntity = self.Inventory.getEntity()
        slots = InventoryEntity.getSlots()
        slot = slots[slotId]

        return slot
        pass

    def _onSlotMouseEnterFilter(self, inventoryObject, item):
        if self.Inventory is not inventoryObject:
            return False
            pass

        itemEntity = item.getEntity()

        spriteCenter = itemEntity.getSpriteCenter()

        itemEntity.coordinate(spriteCenter)

        InventoryItemSelection = DefaultManager.getDefaultFloat("InventoryItemSelection", 1.3)
        itemEntity.setScale((InventoryItemSelection, InventoryItemSelection, 1.0))

        return False
        pass

    def _onSlotMouseLeaveFilter(self, inventoryObject, item):
        if self.Inventory is not inventoryObject:
            return False
            pass

        itemEntity = item.getEntity()

        spriteCenter = itemEntity.getSpriteCenter()

        itemEntity.coordinate((-spriteCenter[0], -spriteCenter[1]))

        InventoryItemScale = DefaultManager.getDefaultFloat("InventoryItemScale", 1.3)
        itemEntity.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        return False
        pass

    pass
