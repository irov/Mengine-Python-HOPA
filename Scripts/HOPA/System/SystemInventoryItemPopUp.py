from Foundation.System import System

from HOPA.ItemManager import ItemManager


class SystemInventoryItemPopUp(System):
    def __init__(self):
        super(SystemInventoryItemPopUp, self).__init__()
        pass

    def _onParams(self):
        super(SystemInventoryItemPopUp, self).__init__()

        self.Inventory = params.get("Inventory")

        self.MouseEnterID = params.get("MouseEnterID")
        self.MouseLeaveID = params.get("MouseLeaveID")
        pass

    def _onInitialize(self):
        super(SystemInventoryItemPopUp, self)._onInitialize()
        pass

    def _onRun(self):
        self.addObserver(self.MouseEnterID, self._onMouseEnterID)
        pass

    def _onStop(self):
        pass

    def _onMouseEnterID(self, inventory, slotID):
        if self.Inventory is not inventory:
            return False
            pass

        slot = self.Inventory.getSlot(slotID)

        ItemName = slot.item.name

        tipItemId = ItemManager.findItemTipId(ItemName)

        with TaskManager.createTaskChain() as tc:
            TipItemShowTime = DefaultManager.getDefaultFloat("TipItemShowTime", 0.0)
            TipItemShowTime *= 1000  # speed fix
            tc.addTask("TaskTipItemPlay", GroupName="TipItem", TipItemID=tipItemId, DelayTime=TipItemShowTime)
            pass

        Mengine.soundPlay("ButtonClicked", False, None)
        pass

    pass
