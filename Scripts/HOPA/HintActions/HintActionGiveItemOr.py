from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.ItemManager import ItemManager

class HintActionGiveItemOr(MixinObject, HintActionMultiTarget):
    def _onParams(self, params):
        super(HintActionGiveItemOr, self)._onParams(params)

        self.ItemNames = params["ItemNames"]
        self.InventoryItem = None
        pass

    def _getHintObject(self):
        return self.Object
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        for name in self.ItemNames[:]:
            InventoryItem = ItemManager.getItemInventoryItem(name)
            if self.Inventory.hasInventoryItem(InventoryItem) is True:
                self.InventoryItem = InventoryItem
                return True
                pass
            pass

        return False
        pass

    def _onAction(self, hint):
        # print "HintActionGiveItemOr _onAction", self.InventoryItem
        # with TaskManager.createTaskChain(Name = "HintActionUseInventoryItem_Scrolling") as tc:
        #     PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
        #     tc.addTask(PolicyInventoryScrolling, InventoryItem = self.InventoryItem)
        #     tc.addTask("TaskFunction", Fn = self.showHint)
        #     pass
        # pass

        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo1 = Sprite.getWorldImageCenter()

        PlaceObjectType = self.Object.getType()

        if PlaceObjectType == "ObjectItem":
            ItemEntity = self.Object.getEntity()
            Sprite = ItemEntity.getSprite()

            PositionTo2 = Sprite.getWorldImageCenter()
            pass

        else:
            hintPoint = self.Object.calcWorldHintPoint()
            if hintPoint is not None:
                PositionTo2 = hintPoint
                pass
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()
                pass
            pass
        self.showHint(PositionTo1,
            PositionTo2)  # with TaskManager.createTaskChain(Name = "HintActionUseInventoryItem_Hint") as tc:  #         PolicyHintWay = PolicyManager.getPolicy("HintWay")  #         tc.addTask(PolicyHintWay, Position = PositionTo1)  #         PolicyHintWayInterrupt = PolicyManager.getPolicy("HintWayInterrupt")  #         tc.addCallback(self.appendInterruptCb,PolicyHintWayInterrupt)  #  #         with tc.addParallelTask(2) as ( tc_target, tc_way):  #             PolicyHintInventoryTargetInterrupt = PolicyManager.getPolicy("HintInventoryTargetInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTarget = PolicyManager.getPolicy("HintInventoryTarget")  #             tc_target.addTask(PolicyHintInventoryTarget, Position = PositionTo1)  #             tc_target.addTask(PolicyHintInventoryTargetInterrupt)  #             tc_target.addCallback(self.removeInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTargetLoop = PolicyManager.getPolicy("HintInventoryTargetLoop")  #             tc_target.addTask(PolicyHintInventoryTargetLoop, Position = PositionTo1)  #  #             PolicyHintInventoryTargetLoopInterrupt = PolicyManager.getPolicy("HintInventoryTargetLoopInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetLoopInterrupt)  #  #             tc_way.addTask(PolicyHintWayInterrupt)  #             tc_way.addCallback(self.removeInterruptCb,PolicyHintWayInterrupt)  #  #             PolicyHintWay = PolicyManager.getPolicy("HintWay")  #             tc_way.addTask(PolicyHintWay, Point = PositionTo1, Position = PositionTo2)  #             tc_way.addCallback(self.appendInterruptCb,PolicyHintWayInterrupt)  #             with tc_way.addParallelTask(2) as (tc_way2, tc_target2):  #                 tc_way2.addTask(PolicyHintWayInterrupt)  #                 tc_way2.addCallback(self.removeInterruptCb,PolicyHintWayInterrupt)  #  #                 PolicyHintTargetInterrupt = PolicyManager.getPolicy("HintTargetInterrupt")  #                 tc_target2.addCallback(self.appendInterruptCb,PolicyHintTargetInterrupt)  #  #                 PolicyHintTarget = PolicyManager.getPolicy("HintTarget")  #                 tc_target2.addTask(PolicyHintTarget, Position = PositionTo2)  #  #                 tc_target2.addTask(PolicyHintTargetInterrupt)  #                 tc_target2.addCallback(self.removeInterruptCb,PolicyHintTargetInterrupt)  #  #                 PolicyHintTargetLoop = PolicyManager.getPolicy("HintTargetLoop")  #                 tc_target2.addTask(PolicyHintTargetLoop, Position = PositionTo2)  #  #                 PolicyHintTargetLoopInterrupt = PolicyManager.getPolicy("HintTargetLoopInterrupt")  #                 tc_target2.addCallback(self.appendInterruptCb,PolicyHintTargetLoopInterrupt)  #                 pass  #             pass  #         tc.addTask("TaskFunction", Fn = self.setEnd)  #         pass  #     pass  #  #  # def _onEnd(self):  #     if TaskManager.existTaskChain("HintActionUseInventoryItem_Scrolling") is True:  #         TaskManager.cancelTaskChain("HintActionUseInventoryItem_Scrolling")  #         pass  #  #     if TaskManager.existTaskChain("HintActionUseInventoryItem_Hint") is True:  #         TaskManager.cancelTaskChain("HintActionUseInventoryItem_Hint")  #         pass  #  #     if len(self.listInterrupt) == 0:  #         return  #  #     with TaskManager.createTaskChain(Cb = self.listInterruptClean) as tc:  #         with tc.addParallelTask(len(self.listInterrupt)) as tc_chains:  #             for tc_chain, policyName in zip(tc_chains, self.listInterrupt):  #                 tc_chain.addTask(policyName)  #                 pass  #             pass  #         pass  #  #     pass  # pass