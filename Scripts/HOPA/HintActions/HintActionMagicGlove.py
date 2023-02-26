from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault

class HintActionMagicGlove(MixinObject, HintActionDefault):

    def _onParams(self, params):
        super(HintActionMagicGlove, self)._onParams(params)
        self.rune_id = params["Rune_ID"]
        self.demon_object = DemonManager.getDemon('MagicGlove')

    def _getHintObject(self):
        return self.demon_object

    def _onCheck(self):
        if self.rune_id in self.demon_object.getParam("Runes"):
            return True
        return False

    def _getHintPosition(self, demon_object):
        entity_object = demon_object.getEntity()
        hotspot = entity_object.getCurrentStateButton()
        pos = hotspot.getCurrentMovieSocketCenter()
        return pos

    # def _onAction(self, hint):  #     self.showHint()  #     pass  #  # def showHint(self):  #     print "showHint"  #     # ItemEntity = self.Item.getEntity()  #     # Sprite = ItemEntity.getSprite()  #     #  #     # PositionTo1 = Sprite.getWorldImageCenter()  #     # Quest = QuestManager.createLocalQuest("Mahjong", SceneName=SceneName, GroupName=GroupName, Object1=btn1,  #     #                                       Object2=btn2)  #     if self.DemonMagicGlove.getParam("State") != "Ready":  #         entity = self.Object.getEntity()  #         hotspot = entity.getHotSpot()  #         PositionTo1= hotspot.getWorldPolygonCenter()  #     else:  #         PositionTo1=self.DemonMagicGlove.getParam("Point")  #  #     with TaskManager.createTaskChain(Name = "HintActionMagicGlove") as tc:  #         PolicyHintWay = PolicyManager.getPolicy("HintWay")  #         tc.addTask(PolicyHintWay, Position = PositionTo1)  #         PolicyHintWayInterrupt = PolicyManager.getPolicy("HintWayInterrupt")  #         tc.addCallback(self.appendInterruptCb,PolicyHintWayInterrupt)  #  #         with tc.addParallelTask(2) as ( tc_target, tc_way):  #             PolicyHintInventoryTargetInterrupt = PolicyManager.getPolicy("HintInventoryTargetInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTarget = PolicyManager.getPolicy("HintInventoryTarget")  #             tc_target.addTask(PolicyHintInventoryTarget, Position = PositionTo1)  #             tc_target.addTask(PolicyHintInventoryTargetInterrupt)  #             tc_target.addCallback(self.removeInterruptCb,PolicyHintInventoryTargetInterrupt)  #  #             PolicyHintInventoryTargetLoop = PolicyManager.getPolicy("HintInventoryTargetLoop")  #             tc_target.addTask(PolicyHintInventoryTargetLoop, Position = PositionTo1)  #  #             PolicyHintInventoryTargetLoopInterrupt = PolicyManager.getPolicy("HintInventoryTargetLoopInterrupt")  #             tc_target.addCallback(self.appendInterruptCb,PolicyHintInventoryTargetLoopInterrupt)  #  #             tc_way.addTask(PolicyHintWayInterrupt)  #             tc_way.addCallback(self.removeInterruptCb,PolicyHintWayInterrupt)  #             pass  #         tc.addTask("TaskFunction", Fn = self.setEnd)  #         pass  #     pass  #  #  # def _onEnd(self):  #     if TaskManager.existTaskChain("HintActionMagicGlove") is True:  #         TaskManager.cancelTaskChain("HintActionMagicGlove")  #         pass  #  #     if len(self.listInterrupt) == 0:  #         return  #  #     with TaskManager.createTaskChain(Cb = self.listInterruptClean) as tc:  #         with tc.addParallelTask(len(self.listInterrupt)) as tc_chains:  #             for tc_chain, policyName in zip(tc_chains, self.listInterrupt):  #                 tc_chain.addTask(policyName)  #                 pass  #             pass  #         pass  #  #     pass  # pass