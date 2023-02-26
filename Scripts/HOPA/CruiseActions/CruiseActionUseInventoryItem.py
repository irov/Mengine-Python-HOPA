from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionUseInventoryItem(MixinObject, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionUseInventoryItem, self)._onParams(params)
        self.Inventory = DemonManager.getDemon("Inventory")
        self.InventoryItem = params["InventoryItem"]
        self.sem_done_scroll = Semaphore(False, "done_scroll")
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionUseInventoryItem')

    def _onCheck(self):
        if self.Inventory.hasInventoryItem(self.InventoryItem) is True:
            return self.InventoryItem.checkCount()
        return False

    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionUseInventoryItem_Scrolling") is True:
            TaskManager.cancelTaskChain("CruiseActionUseInventoryItem_Scrolling")

        if TaskManager.existTaskChain("CruiseActionUseInventoryItem_Cruise") is True:
            TaskManager.cancelTaskChain("CruiseActionUseInventoryItem_Cruise")

        with TaskManager.createTaskChain(Name="CruiseActionUseInventoryItem_Scrolling") as tc:
            with tc.addRepeatTask() as (tc_repeat, tc_until):
                with tc_repeat.addSwitchTask(2, self.__isDoneScroll) as (tc_scroll, tc_done):
                    tc_scroll.addScope(self.__scopeScrollInventory)

                    tc_done.addSemaphore(self.sem_done_scroll, From=False, To=True)

                tc_until.addSemaphore(self.sem_done_scroll, From=True)

            tc.addFunction(self.showCruise)

    def __isDoneScroll(self, isSkip, cb):
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        if NeedSlotIndex != CurrentSlotIndex:
            cb(isSkip, 0)

        else:
            cb(isSkip, 1)

    def __scopeScrollInventory(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")

        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NeedSlotIndex:
            if NeedSlotIndex > CurrentSlotIndex:
                buttonInv = self.Inventory.getObject("Button_InvRight")

            else:
                buttonInv = self.Inventory.getObject("Button_InvLeft")

            source.addTask("AliasCruiseControlAction", Position=buttonInv.calcWorldHintPoint(), Object=buttonInv)

    def getMultiTargetPosition(self):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()
        PositionTo1 = Sprite.getWorldImageCenter()

        if self.Object is None:
            PositionTo2 = None

        else:
            PlaceObjectType = self.Object.getType()

            if PlaceObjectType == "ObjectItem":
                ItemEntity = self.Object.getEntity()
                Sprite = ItemEntity.getSprite()

                PositionTo2 = Sprite.getWorldImageCenter()

            else:
                if self.Object.hasParam("HintPoint") is True:
                    hintPoint = self.Object.calcWorldHintPoint()

                    if hintPoint is not None:
                        PositionTo2 = hintPoint

                    else:
                        ObjectEntity = self.Object.getEntity()
                        HotSpot = ObjectEntity.getHotSpot()

                        PositionTo2 = HotSpot.getWorldPolygonCenter()

                else:
                    ObjectEntity = self.Object.getEntity()

                    Sprite = ObjectEntity.getSprite()
                    PositionTo2 = Sprite.getWorldImageCenter()

        return PositionTo1, PositionTo2

    def showCruise(self):
        PositionTo1, PositionTo2 = self.getMultiTargetPosition()

        with TaskManager.createTaskChain(Name="CruiseActionUseInventoryItem_Cruise") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo1, Object=self.InventoryItem)

            if PositionTo2 is not None:
                tc.addTask("AliasCruiseControlAction", Position=PositionTo2, Object=self.Object)

            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))