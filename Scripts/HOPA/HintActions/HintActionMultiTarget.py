from Foundation.DefaultManager import DefaultManager
from Foundation.Task.MixinGroup import MixinGroup
from Foundation.TaskManager import TaskManager
from HOPA.HintAction import HintAction


class HintActionMultiTarget(MixinGroup, HintAction):
    def _onInitialize(self):
        super(HintActionMultiTarget, self)._onInitialize()
        self.hintObject = self._getHintObject()
        self.Movie2_HintTarget = None
        self.Movie2_HintWay = None
        self.Movie2_HintInventoryTarget = None
        self.Working = False
        self.timer = 400.0
        pass

    def __ClickEnd(self):
        self._onEnd()
        return False

    def Setup(self):
        self.Movie2_HintTarget = self.Create_Movie("Movie2_HintTarget")
        self.Movie2_HintWay = self.Create_Movie("Movie2_HintWay")
        self.Movie2_HintInventoryTarget = self.Create_Movie("Movie2_HintInventoryTarget")

    def getMultiHintPosition(self):
        return None

    def Bezier_pos(self, P0, P2):
        p1x = P0[0] if P0[1] > P2[1] else P2[0]
        p1y = P2[1] if P0[1] > P2[1] else P0[1]
        P1_5 = (p1x, p1y)
        return P1_5

    def Check_Action(self, source):
        if self.Movie2_HintTarget == None or self.Movie2_HintWay == None or self.Movie2_HintInventoryTarget == None:
            source.addDelay(self.timer)
            source.addFunction(self.destroy_all_movies)
            source.addFunction(self.Setup)

    def scopeSetTargetPos(self, souce, node, P1):
        pos = node.getWorldPosition()
        posTo = (P1.x, pos.y + 40)
        souce.addTask("TaskObjectSetPosition", Object=self.Movie2_HintInventoryTarget, Value=posTo)

    def scopeAction(self, source, P1, P2, Offset):
        speed = DefaultManager.getDefaultFloat("HintWaySpeed", 600) / 1000.0
        P0 = self.getStart_Position()

        node = self.getFollow_Node()
        if node is None:
            P1_5 = self.Bezier_pos(P0, P1)
        P2_5 = self.Bezier_pos(P1, P2)

        source.addTask("TaskObjectSetPosition", Object=self.Movie2_HintWay, Value=P0)
        if node is None:
            source.addTask("TaskObjectSetPosition", Object=self.Movie2_HintInventoryTarget, Value=P1)
        source.addTask("TaskObjectSetPosition", Object=self.Movie2_HintTarget, Value=P2)

        source.addTask("TaskMovie2Play", Movie2=self.Movie2_HintWay, Loop=True, Wait=False)
        if node is None:
            source.addTask("AliasObjectBezier2To", Object=self.Movie2_HintWay, Point1=P1_5, To=P1, Speed=speed)
        else:
            source.addTask("TaskNodeBezier2WorldFollow", Follow=node,
                           Node=self.Movie2_HintWay.getEntityNode(), Speed=speed, Offset=Offset)
            source.addScope(self.scopeSetTargetPos, node, P1)

        with source.addParallelTask(2) as (tc_way, tc_target):
            tc_way.addTask("AliasObjectBezier2To", Object=self.Movie2_HintWay, Point1=P2_5, To=P2, Speed=speed / 1.35)

            tc_target.addTask("TaskMovie2Play", Movie2=self.Movie2_HintInventoryTarget, Loop=False, Wait=True)
            tc_target.addTask("TaskMovie2Stop", Movie2=self.Movie2_HintInventoryTarget)
            with tc_way.addParallelTask(2) as (tc_way2, tc_target2):
                tc_way2.addTask("TaskMovie2Interrupt", Movie2=self.Movie2_HintWay)

                tc_target2.addTask("TaskMovie2Play", Movie2=self.Movie2_HintTarget, Loop=False, Wait=True)
                tc_target2.addTask("TaskMovie2Stop", Movie2=self.Movie2_HintTarget)
                tc_target2.addTask("TaskNotify", ID=Notificator.onHintActionItemCollectEnd)

    def showHint(self, P1, P2, Offset=(0.0, 0.0)):
        if TaskManager.existTaskChain("HintAction_onEnd") is True:
            TaskManager.cancelTaskChain("HintAction_onEnd")

        if TaskManager.existTaskChain("HintActionDefault") is True:
            TaskManager.cancelTaskChain("HintActionDefault")

        with TaskManager.createTaskChain(Name="HintActionDefault", Cb=self._onEnd) as tc:
            tc.addFunction(self.Setup)
            tc.addScope(self.Check_Action)
            tc.addScope(self.scopeAction, P1, P2, Offset)

    def destroy_all_movies(self):
        self.Movie2_HintTarget = self.destroy_movie("Movie2_HintTarget")
        self.Movie2_HintWay = self.destroy_movie("Movie2_HintWay")
        self.Movie2_HintInventoryTarget = self.destroy_movie("Movie2_HintInventoryTarget")

    def Clean_Full(self):
        if TaskManager.existTaskChain("HintActionDefault") is True:
            TaskManager.cancelTaskChain("HintActionDefault")
            pass
        self.destroy_all_movies()

        self.Working = False

    def _onEnd(self, someargs=None):
        if self.Working:
            return
        else:
            self.Working = True
        if TaskManager.existTaskChain("HintAction_onEnd") is True:
            TaskManager.cancelTaskChain("HintAction_onEnd")

        if self.Movie2_HintWay is not None:
            with TaskManager.createTaskChain(Name="HintAction_onEnd") as tc:
                with tc.addParallelTask(3) as (tc_way, tc_target, tc_target2):
                    tc_way.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintWay, To=0.0, Time=self.timer)
                    tc_target.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintTarget, To=0.0, Time=self.timer)
                    tc_target2.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintInventoryTarget, To=0.0, Time=self.timer)
                tc.addFunction(self.Clean_Full)
                tc.addFunction(self.setEnd)
