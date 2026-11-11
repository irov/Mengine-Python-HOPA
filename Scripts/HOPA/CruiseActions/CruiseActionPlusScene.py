from Foundation.DemonManager import DemonManager
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

    def _onAction(self, source):
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

        with source.addRepeatTask() as (tc_repeat, tc_until):
            with tc_repeat.addSwitchTask(2, __isDoneScroll) as (tc_scroll, tc_done):
                tc_scroll.addTask("AliasCruiseControlAction",
                                  Position=InventoryButtonPosition, Object=self.getInvButton())
                tc_scroll.addListener(Notificator.onInventorySlotsShiftEnd)

                tc_done.addSemaphore(self.sem_done_scroll, From=0, To=1)

            tc_until.addSemaphore(self.sem_done_scroll, From=1)

        source.addScope(self.showCruise)

    def showCruise(self, source):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo = Sprite.getWorldImageCenter()

        with source.addParallelTask(2) as (check, run):
            check.addListener(Notificator.onQuestEnd, Filter=lambda quest: quest == self.Quest)
            run.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.InventoryItem)

        source.addDelay(1500.0)
        source.addNotify(Notificator.onCruiseActionEnd, self)

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
