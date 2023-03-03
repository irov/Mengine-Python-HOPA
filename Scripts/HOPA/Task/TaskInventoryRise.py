from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias


class TaskInventoryRise(TaskAlias):
    def _onParams(self, params):
        super(TaskInventoryRise, self)._onParams(params)

        self.Holder = params.get("Holder")
        self.InventoryItem = params.get("InventoryItem", None)
        self.slot = params.get("slot", None)
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onInventoryRise)

    def demonizer(self, inventory_Name):
        demon_Inventory = DemonManager.getDemon(inventory_Name)
        if demon_Inventory.isActive() is False:
            return None
        entity_Inventory = demon_Inventory.getEntity()
        return entity_Inventory

    def Item_Position(self):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()
        Position = Sprite.getWorldImageCenter()

        return Position

    def Slot_Position(self):
        Position = self.slot.getPoint()
        return Position
