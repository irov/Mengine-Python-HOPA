from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.ItemManager import ItemManager


class CruiseActionItemUseFittingInventoryItem(MixinItem, CruiseAction):
    def __init__(self):
        super(CruiseActionItemUseFittingInventoryItem, self).__init__()

        self.InventoryItem = None
        self.SocketName = None

        self.Inventory = DemonManager.getDemon("FittingInventory")

    def _onParams(self, params):
        super(CruiseActionItemUseFittingInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]

    def _onCheck(self):
        if CruiseControlManager.inBlackList(self.Item) is True:
            return False

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False

        return True

    def _onAction(self, cruise):
        Inventory = DemonManager.getDemon("FittingInventory")

        CurrentSlotIndex = Inventory.getParam("CurrentSlotIndex")
        SlotCount = Inventory.getParam("SlotCount")

        InventoryItemIndex = Inventory.getInventoryItemIndex(self.InventoryItem)
        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        Point = cruise.getPoint()

        with TaskManager.createTaskChain() as tc:
            if CurrentSlotIndex != NewSlotIndex:
                with GuardBlockInput(tc) as guard_tc:
                    guard_tc.addTask("TaskInventorySlotsHideInventoryItem", Inventory=Inventory)
                    guard_tc.addTask("TaskInventoryCurrentSlotIndex", Inventory=Inventory, Value=NewSlotIndex)
                    pass
                pass

            InventoryItem = ItemManager.findItemInventoryItem(self.InventoryItem)
            InventoryItemEntity = InventoryItem.getEntity()
            Sprite = InventoryItemEntity.getSprite()
            P2 = Sprite.getWorldImageCenter()
            ItemEntity = self.Item.getEntity()
            Sprite = ItemEntity.getSprite()
            NP2 = Sprite.getWorldImageCenter()

            tc.addTask("AliasCruiseControlAction", Position=Point)
            tc.addTask("AliasCruiseControlAction", Position=P2, Object=InventoryItem)
            tc.addTask("AliasCruiseControlAction", Position=NP2, Object=self.Item)

            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass

    def _onEnd(self):
        super(CruiseActionItemUseFittingInventoryItem, self)._onEnd()
        pass

    pass
