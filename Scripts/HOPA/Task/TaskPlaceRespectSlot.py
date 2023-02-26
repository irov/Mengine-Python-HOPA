from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ItemManager import ItemManager

class TaskPlaceRespectSlot(MixinObserver, Task):

    def _onParams(self, params):
        super(TaskPlaceRespectSlot, self)._onParams(params)
        self.ItemNameInInventory = params.get("Item")
        self.ObjectToPlace = params.get("Object")
        pass

    def _onInitialize(self):
        super(TaskPlaceRespectSlot, self)._onInitialize()
        pass

    def _onRun(self):
        InventoryObject = DemonManager.getDemon("Inventory")
        InventoryInst = InventoryObject.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemNameInInventory)
        SlotIns = InventoryInst.findSlot(InventoryItem)
        if SlotIns is None:
            self.log("SlotIns is None, didnt find %s in Inventory" % self.ItemNameInInventory)
            return True
            pass
        point = SlotIns.getPoint()
        slotPosition = point.getWorldPosition()
        shiftX = slotPosition.x  # nameTuple
        positionOfObject = self.ObjectToPlace.getPosition()
        self.ObjectToPlace.setOrigin((-shiftX, 0))
        self.ObjectToPlace.setPosition(positionOfObject)
        return True
        pass
    pass