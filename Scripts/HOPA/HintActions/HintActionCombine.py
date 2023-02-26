from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget

class HintActionCombine(HintActionMultiTarget):
    def __init__(self):
        super(HintActionCombine, self).__init__()
        pass

    def _onParams(self, params):
        super(HintActionCombine, self)._onParams(params)

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

    def _onAction(self, hint):
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
        self.showHint(PositionTo1, PositionTo2)

    #     with TaskManager.createTaskChain(Name = "HintActionCombinePlay") as tc:  #         PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")  #         tc.addTask(PolicyInventoryScrolling, InventoryItem = self.AttachInventoryItem)  #  #         PolicyHintWay = PolicyManager.getPolicy("HintWay")  #         tc.addTask(PolicyHintWay, Position = PositionTo1)  #  #         PolicyHintWayInterrupt = PolicyManager.getPolicy("HintWayInterrupt")  #         tc.addCallback(self.appendInterruptCb,PolicyHintWayInterrupt)  #  #         with tc.addParallelTask(2) as (tc_way, tc_target):  #             PolicyHintWayInterrupt = PolicyManager.getPolicy("HintWayInterrupt")  #             tc_way.addTask(PolicyHintWayInterrupt)  #             tc_way.addCallback(self.removeInterruptCb,PolicyHintWayInterrupt)  #  #             PolicyHintInventoryTargetInterrupt = PolicyManager.getPolicy("HintInventoryTargetInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTarget= PolicyManager.getPolicy("HintInventoryTarget")  #             tc_target.addTask(PolicyHintInventoryTarget, Position = PositionTo1)  #  #             tc_target.addTask(PolicyHintInventoryTargetInterrupt)  #             tc_target.addCallback(self.removeInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTargetLoop = PolicyManager.getPolicy("HintInventoryTargetLoop")  #             tc_target.addTask(PolicyHintInventoryTargetLoop, Position = PositionTo1)  #  #             PolicyHintInventoryTargetLoopInterrupt = PolicyManager.getPolicy("HintInventoryTargetLoopInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetLoopInterrupt)  #             pass  #  #         PolicyHintWay = PolicyManager.getPolicy("HintWay")  #         tc.addTask(PolicyHintWay, Point = PositionTo1, Position = PositionTo2)  #         tc.addCallback(self.appendInterruptCb,PolicyHintWayInterrupt)  #  #         with tc.addParallelTask(2) as (tc_way2, tc_target2):  #             tc_way2.addTask(PolicyHintWayInterrupt)  #             tc_way2.addCallback(self.removeInterruptCb,PolicyHintWayInterrupt)  #  #             PolicyHintTargetInterrupt = PolicyManager.getPolicy("HintTargetInterrupt")  #             tc_target2.addCallback(self.appendInterruptCb,PolicyHintTargetInterrupt)  #  #             PolicyHintTarget = PolicyManager.getPolicy("HintTarget")  #             tc_target2.addTask(PolicyHintTarget, Position = PositionTo2)  #  #             tc_target2.addTask(PolicyHintTargetInterrupt)  #             tc_target2.addCallback(self.removeInterruptCb,PolicyHintTargetInterrupt)  #  #             PolicyHintTargetLoop = PolicyManager.getPolicy("HintTargetLoop")  #             tc_target2.addTask(PolicyHintTargetLoop, Position = PositionTo2)  #  #             PolicyHintTargetLoopInterrupt = PolicyManager.getPolicy("HintTargetLoopInterrupt")  #             tc_target2.addCallback(self.appendInterruptCb,PolicyHintTargetLoopInterrupt)  #             pass  #         tc.addTask("TaskFunction", Fn = self.setEnd)  #         pass  #  #     with TaskManager.createTaskChain(Name = "HintActionCombine", Cb = self.listInterruptClean) as tc:  #         tc.addTask("TaskInventoryCarriageChange", Inventory = self.Inventory)  #         with tc.addParallelTask(len(self.listInterrupt)) as tc_chains:  #             for tc_chain, policyName in zip(tc_chains, self.listInterrupt):  #                 tc_chain.addTask(policyName)  #                 pass  #             pass  #         pass  #     pass  #  # def _onEnd(self):  #     if TaskManager.existTaskChain("HintActionCombinePlay") is True:  #         TaskManager.cancelTaskChain("HintActionCombinePlay")  #         pass  #     if TaskManager.existTaskChain("HintActionCombine") is True:  #         TaskManager.cancelTaskChain("HintActionCombine")  #         pass  #  #     if len(self.listInterrupt) == 0:  #         return  #  #     with TaskManager.createTaskChain( Cb = self.listInterruptClean) as tc:  #         with tc.addParallelTask(len(self.listInterrupt)) as tc_chains:  #             for tc_chain, policyName in zip(tc_chains, self.listInterrupt):  #                 tc_chain.addTask(policyName)  #                 pass  #             pass  #         pass  #     pass  # pass