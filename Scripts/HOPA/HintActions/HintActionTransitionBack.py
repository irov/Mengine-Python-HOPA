from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionTransitionBack(MixinTransition, HintActionDefault):
    def _onInitialize(self):
        super(HintActionTransitionBack, self)._onInitialize()
        self.hintObject = self._getHintObject()
        self.Movie2_HintTarget = None
        self.Movie2_HintWay = None
        self.Movie2_HintInventoryTarget = None
        self.Working = False
        self.timer = 400.0

    def _getHintObject(self):
        return self.Transition

    def _onCheck(self):
        return EnigmaManager.getSceneActiveEnigma() is None

    def _getHintPosition(self, Object):
        demon = GroupManager.getObject("TransitionBack", "Demon_TransitionBack")
        demon_node = demon.getEntityNode()
        effect = GroupManager.getObject("HintEffect", "Movie2_TransitionBack")
        effect_Node = effect.getEntityNode()

        if GroupManager.hasObject("TransitionBack", "Point_Effect") is True:
            Point_Effect = GroupManager.getObject("TransitionBack", "Point_Effect")
            demon_node.addChild(effect_Node)

            Position = Point_Effect.getPosition()

            return Position

        return 0.0, 0.0, 0.0

    def Setup(self):
        self.Movie2_HintTarget = self.Create_Movie("Movie2_HintTarget")
        self.Movie2_HintWay = self.Create_Movie("Movie2_HintWay")

    def Check_Action(self, source):
        if self.Movie2_HintTarget is None or self.Movie2_HintWay is None:
            source.addDelay(self.timer)
            source.addFunction(self.destroy_all_movies)
            source.addFunction(self.Setup)

    def scopeAction(self, tc):
        demon = GroupManager.getObject("TransitionBack", "Demon_TransitionBack")
        demon_node = demon.getEntityNode()
        self.effect = GroupManager.getObject("HintEffect", "Movie2_TransitionBack")
        effect_Node = self.effect.getEntityNode()
        if GroupManager.hasObject("TransitionBack", "Point_Effect") is True:
            Point_Effect = GroupManager.getObject("TransitionBack", "Point_Effect")
            demon_node.addChild(effect_Node)

            Position = Point_Effect.getPosition()
            effect_Node.setWorldPosition(Position)
            self.effect.setPosition(Position)

        speed = DefaultManager.getDefaultFloat("HintWaySpeed", 600) / 1000.0

        P2 = self._getHintPosition(self.hintObject)
        P0 = self.getStart_Position()
        p1x = P2[1] + abs(P2[1] - P0[1])
        p1y = P2[0] / 3.0

        P1 = (p1x, p1y)
        tc.addTask("TaskObjectSetPosition", Object=self.Movie2_HintWay, Value=P0)
        tc.addTask("TaskMovie2Play", Movie2=self.Movie2_HintWay, Loop=True, Wait=False)
        tc.addTask("AliasObjectBezier2To", Object=self.Movie2_HintWay, Point1=P1, To=P2, Speed=speed)

        tc.addEnable(self.effect)
        with tc.addParallelTask(3) as (tc_way, tc_target, tc_target_Alpha):
            tc_way.addTask("TaskMovie2Interrupt", Movie2=self.Movie2_HintWay)
            tc_way.addTask("TaskMovie2Stop", Movie2=self.Movie2_HintWay)
            tc_target_Alpha.addTask("TaskNodeAlphaTo", Node=effect_Node, From=0.0, To=1.0, Time=self.timer * 2)
            tc_target.addTask("TaskMovie2Play", Movie2=self.effect, Wait=True, Loop=True, AutoEnable=True)

    def _onAction(self, hint):
        if TaskManager.existTaskChain("HintAction_onEnd") is True:
            TaskManager.cancelTaskChain("HintAction_onEnd")

        if TaskManager.existTaskChain("HintActionDefault") is True:
            TaskManager.cancelTaskChain("HintActionDefault")

        with TaskManager.createTaskChain(Name="HintActionDefault", Cb=self._onEnd) as tc:
            tc.addFunction(self.Setup)
            tc.addScope(self.Check_Action)
            tc.addScope(self.scopeAction)

    def destroy_all_movies(self):
        self.Movie2_HintTarget = self.destroy_movie("Movie2_HintTarget")
        self.Movie2_HintWay = self.destroy_movie("Movie2_HintWay")

    def Clean_Full(self):
        if TaskManager.existTaskChain("HintActionDefault") is True:
            TaskManager.cancelTaskChain("HintActionDefault")

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
                with tc.addParallelTask(2) as (tc_way, tc_target):
                    tc_way.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintWay, To=0.0, Time=self.timer)
                    tc_target.addTask("AliasObjectAlphaTo", Object=self.effect, To=0.0, Time=self.timer)

                tc.addFunction(self.Clean_Full)
                tc.addFunction(self.setEnd)
