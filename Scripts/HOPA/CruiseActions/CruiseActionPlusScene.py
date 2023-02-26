from Foundation.DemonManager import DemonManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionPlusScene(CruiseAction):
    def _onParams(self, params):
        super(CruiseActionPlusScene, self)._onParams(params)
        self.InventoryItem = params['InventoryItem']
        self.Inventory = DemonManager.getDemon("Inventory")
        self.sem_done_scroll = Semaphore(0, "done_scroll")

    def _onCheck(self):
        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False

        return True

    def onAction(self):
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        InventoryButtonPosition = self.getInvButtonPosition()

        def __isDoneScroll(isSkip, cb):
            CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
            if NeedSlotIndex != CurrentSlotIndex:
                cb(isSkip, 0)
            else:
                cb(isSkip, 1)

        if TaskManager.existTaskChain("CruiseActionScenePlus_Scrolling"):
            TaskManager.cancelTaskChain("CruiseActionScenePlus_Scrolling")

        with TaskManager.createTaskChain(Name="CruiseActionScenePlus_Scrolling") as tc:
            with tc.addRepeatTask() as (tc_repeat, tc_until):
                with tc_repeat.addSwitchTask(2, __isDoneScroll) as (tc_scroll, tc_done):
                    tc_scroll.addTask("AliasCruiseControlAction", Position=InventoryButtonPosition, Object=self.getInvButton())
                    tc_scroll.addTask("TaskListener", ID=Notificator.onInventorySlotsShiftEnd)

                    tc_done.addSemaphore(self.sem_done_scroll, From=0, To=1)

                tc_until.addSemaphore(self.sem_done_scroll, From=1)

            tc.addTask("TaskFunction", Fn=self.showCruise)

    def showCruise(self):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo = Sprite.getWorldImageCenter()

        if TaskManager.existTaskChain("CruiseActionScenePlus_Cruise"):
            TaskManager.cancelTaskChain("CruiseActionScenePlus_Cruise")

        with TaskManager.createTaskChain(Name="CruiseActionScenePlus_Cruise") as tc:
            with tc.addParallelTask(2) as (check, run):
                check.addListener(Notificator.onQuestEnd, Filter=lambda quest: quest == self.Quest)
                run.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.InventoryItem)

            tc.addDelay(1500.0)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def getInvButton(self):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NeedSlotIndex:
            if NeedSlotIndex > CurrentSlotIndex:
                return self.Inventory.getObject("Button_InvRight")
            elif NeedSlotIndex < CurrentSlotIndex:
                return self.Inventory.getObject("Button_InvLeft")

    def getInvButtonPosition(self):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NeedSlotIndex:
            buttonInv = None

            if NeedSlotIndex > CurrentSlotIndex:
                buttonInv = self.Inventory.getObject("Button_InvRight")
            elif NeedSlotIndex < CurrentSlotIndex:
                buttonInv = self.Inventory.getObject("Button_InvLeft")

            if buttonInv is not None:
                buttonInvEntity = buttonInv.getEntity()
                buttonInvSprite = buttonInvEntity.getSprite()
                PositionButtonInv = buttonInvSprite.getWorldImageCenter()
                return PositionButtonInv