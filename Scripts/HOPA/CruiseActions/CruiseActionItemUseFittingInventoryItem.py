from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.MixinObjectTemplate import MixinItem
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

    def _onAction(self, source):
        Inventory = DemonManager.getDemon("FittingInventory")

        CurrentSlotIndex = Inventory.getParam("CurrentSlotIndex")
        SlotCount = Inventory.getParam("SlotCount")

        InventoryItemIndex = Inventory.getInventoryItemIndex(self.InventoryItem)
        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NewSlotIndex:
            with GuardBlockInput(source) as guard_tc:
                guard_tc.addTask("TaskInventorySlotsHideInventoryItem", Inventory=Inventory)
                guard_tc.addTask("TaskInventoryCurrentSlotIndex", Inventory=Inventory, Value=NewSlotIndex)
                pass

        InventoryItem = ItemManager.findItemInventoryItem(self.InventoryItem)
        InventoryItemEntity = InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()
        P2 = Sprite.getWorldImageCenter()
        ItemEntity = self.Item.getEntity()
        Sprite = ItemEntity.getSprite()
        NP2 = Sprite.getWorldImageCenter()

        source.addTask("AliasCruiseControlAction", Position=P2, Object=InventoryItem)
        source.addTask("AliasCruiseControlAction", Position=NP2, Object=self.Item)

        source.addNotify(Notificator.onCruiseActionEnd, self)
        pass

    pass
