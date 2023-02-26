from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionCombine(CruiseAction):
    def __init__(self):
        super(CruiseActionCombine, self).__init__()
        pass

    def _onParams(self, params):
        super(CruiseActionCombine, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.AttachInventoryItem = params.get("AttachInventoryItem")
        self.SlotInventoryItem = params.get("SlotInventoryItem")
        pass

    def _onCheck(self):
        if self.Inventory.hasInventoryItem(self.AttachInventoryItem) is False:
            return False
            pass

        if self.Inventory.hasInventoryItem(self.SlotInventoryItem) is False:
            return False
            pass

        return True
        pass

    def _onAction(self, cruise):
        InventoryItemEntity = self.AttachInventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo1 = Sprite.getWorldImageCenter()

        SlotCount = self.Inventory.getParam("SlotCount")

        AttachInventoryItemIndex = self.Inventory.indexInventoryItem(self.AttachInventoryItem)
        AttachSlotIndex = int(AttachInventoryItemIndex / SlotCount) * SlotCount

        SlotInventoryItemIndex = self.Inventory.indexInventoryItem(self.SlotInventoryItem)
        NewSlotIndex = int(SlotInventoryItemIndex / SlotCount) * SlotCount

        if AttachSlotIndex == NewSlotIndex:
            InventoryItemEntity = self.SlotInventoryItem.getEntity()
            Sprite = InventoryItemEntity.getSprite()

            PositionTo2 = Sprite.getWorldImageCenter()
            pass

        elif AttachSlotIndex < NewSlotIndex:
            Button_InvRight = self.Inventory.getObject("Button_InvRight")
            Button_InvRightEntity = Button_InvRight.getEntity()

            Sprite = Button_InvRightEntity.getSprite()
            PositionTo2 = Sprite.getWorldImageCenter()
            pass

        elif AttachSlotIndex > NewSlotIndex:
            Button_InvLeft = self.Inventory.getObject("Button_InvLeft")
            Button_InvLeftEntity = Button_InvLeft.getEntity()

            Sprite = Button_InvLeftEntity.getSprite()
            PositionTo2 = Sprite.getWorldImageCenter()
            pass

        with TaskManager.createTaskChain(Name="CruiseActionCombinePlay") as tc:
            PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
            tc.addTask(PolicyInventoryScrolling, InventoryItem=self.AttachInventoryItem)

            tc.addTask("AliasCruiseControlAction", Position=PositionTo1)
            tc.addTask("AliasCruiseControlAction", Position=PositionTo2)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass

        pass

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionCombinePlay") is True:
            TaskManager.cancelTaskChain("CruiseActionCombinePlay")
            pass

        pass
    pass