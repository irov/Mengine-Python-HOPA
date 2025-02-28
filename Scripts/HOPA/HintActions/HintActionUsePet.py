from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.HintAction import HintAction


class HintActionUsePet(MixinObject, HintAction):
    def _onParams(self, params):
        super(HintActionUsePet, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        pass

    def _getHintObject(self):
        return self.Object
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        return True
        pass

    def _onAction(self, hint):
        # print "HintActionDefault._onAction:type = %s, "%(self.getType()), self.InventoryItem.getName()

        with TaskManager.createTaskChain(Name="HintActionUsePet_Scrolling") as tc:
            PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling", "PolicyInventoryScrollingDefault")
            tc.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)
            tc.addFunction(self.showHint)
            pass
        pass

    def showHint(self):
        # print "showHint"
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo1 = Sprite.getWorldImageCenter()

        if self.Object.hasParam("HintPoint") is True:
            hintPoint = self.Object.calcWorldHintPoint()
            if hintPoint is not None:
                PositionTo2 = hintPoint
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()
                pass
            pass
        else:
            return False
        pass

        with TaskManager.createTaskChain(Name="HintActionUsePet_Hint") as tc:
            PolicyHintWay = PolicyManager.getPolicy("HintWay")
            tc.addTask(PolicyHintWay, Position=PositionTo1)
            PolicyHintWayInterrupt = PolicyManager.getPolicy("HintWayInterrupt")
            tc.addCallback(self.appendInterruptCb, PolicyHintWayInterrupt)

            with tc.addParallelTask(2) as (tc_target, tc_way):
                PolicyHintInventoryTargetInterrupt = PolicyManager.getPolicy("HintInventoryTargetInterrupt")
                tc_target.addCallback(self.appendInterruptCb, PolicyHintInventoryTargetInterrupt)

                PolicyHintInventoryTarget = PolicyManager.getPolicy("HintInventoryTarget")
                tc_target.addTask(PolicyHintInventoryTarget, Position=PositionTo1)
                tc_target.addTask(PolicyHintInventoryTargetInterrupt)
                tc_target.addCallback(self.removeInterruptCb, PolicyHintInventoryTargetInterrupt)

                PolicyHintInventoryTargetLoop = PolicyManager.getPolicy("HintInventoryTargetLoop")
                tc_target.addTask(PolicyHintInventoryTargetLoop, Position=PositionTo1)

                PolicyHintInventoryTargetLoopInterrupt = PolicyManager.getPolicy("HintInventoryTargetLoopInterrupt")
                tc_target.addCallback(self.appendInterruptCb, PolicyHintInventoryTargetLoopInterrupt)

                tc_way.addTask(PolicyHintWayInterrupt)
                tc_way.addCallback(self.removeInterruptCb, PolicyHintWayInterrupt)

                PolicyHintWay = PolicyManager.getPolicy("HintWay")
                tc_way.addTask(PolicyHintWay, Point=PositionTo1, Position=PositionTo2)
                tc_way.addCallback(self.appendInterruptCb, PolicyHintWayInterrupt)
                with tc_way.addParallelTask(2) as (tc_way2, tc_target2):
                    tc_way2.addTask(PolicyHintWayInterrupt)
                    tc_way2.addCallback(self.removeInterruptCb, PolicyHintWayInterrupt)

                    PolicyHintTargetInterrupt = PolicyManager.getPolicy("HintTargetInterrupt")
                    tc_target2.addCallback(self.appendInterruptCb, PolicyHintTargetInterrupt)

                    PolicyHintTarget = PolicyManager.getPolicy("HintTarget")
                    tc_target2.addTask(PolicyHintTarget, Position=PositionTo2)

                    tc_target2.addTask(PolicyHintTargetInterrupt)
                    tc_target2.addCallback(self.removeInterruptCb, PolicyHintTargetInterrupt)

                    PolicyHintTargetLoop = PolicyManager.getPolicy("HintTargetLoop")
                    tc_target2.addTask(PolicyHintTargetLoop, Position=PositionTo2)

                    PolicyHintTargetLoopInterrupt = PolicyManager.getPolicy("HintTargetLoopInterrupt")
                    tc_target2.addCallback(self.appendInterruptCb, PolicyHintTargetLoopInterrupt)
                    pass
                pass
            tc.addFunction(self.setEnd)
            pass
        pass

    def _onEnd(self):
        if TaskManager.existTaskChain("HintActionUsePet_Scrolling") is True:
            TaskManager.cancelTaskChain("HintActionUsePet_Scrolling")
            pass

        if TaskManager.existTaskChain("HintActionUsePet_Hint") is True:
            TaskManager.cancelTaskChain("HintActionUsePet_Hint")
            pass

        if len(self.listInterrupt) == 0:
            return

        with TaskManager.createTaskChain(Cb=self.listInterruptClean) as tc:
            with tc.addParallelTask(len(self.listInterrupt)) as tc_chains:
                for tc_chain, policyName in zip(tc_chains, self.listInterrupt):
                    tc_chain.addTask(policyName)
