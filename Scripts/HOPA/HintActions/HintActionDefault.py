from Foundation.DefaultManager import DefaultManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.HintAction import HintAction


class HintActionDefault(MixinGroup, HintAction):
    def _onInitialize(self):
        super(HintActionDefault, self)._onInitialize()
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

    def Check_Action(self, source):
        if self.Movie2_HintTarget is None or self.Movie2_HintWay is None:
            source.addDelay(self.timer)
            source.addFunction(self.destroy_movies_by_name)
            source.addFunction(self.Setup)

    def scopeAction(self, tc):
        speed = DefaultManager.getDefaultFloat("HintWaySpeed", 600) / 1000.0

        P2 = self._getHintPosition(self.hintObject)
        P0 = self.getStart_Position()
        p1x = P0[0] if P0[1] > P2[1] else P2[0]
        p1y = P2[1] if P0[1] > P2[1] else P0[1]

        P1 = (p1x, p1y)

        def _scopeTargetPlay(source):
            # fix https://wonderland-games.atlassian.net/browse/CAME2-1079
            # when code reaches this block - one of these movies could be disabled
            with source.addParallelTask(2) as (tc_way, tc_target):
                if self.Movie2_HintWay.entity.isActivate():
                    tc_way.addTask("TaskMovie2Interrupt", Movie2=self.Movie2_HintWay)
                    tc_way.addTask("TaskMovie2Stop", Movie2=self.Movie2_HintWay)
                if self.Movie2_HintTarget.entity.isActivate():
                    tc_target.addTask("TaskMovie2Play", Movie2=self.Movie2_HintTarget, Loop=False, Wait=True)
                    tc_target.addTask("TaskMovie2Stop", Movie2=self.Movie2_HintTarget)

        tc.addTask("TaskObjectSetPosition", Object=self.Movie2_HintWay, Value=P0)
        tc.addTask("TaskObjectSetPosition", Object=self.Movie2_HintTarget, Value=P2)
        tc.addTask("TaskMovie2Play", Movie2=self.Movie2_HintWay, Loop=True, Wait=False)
        tc.addTask("AliasObjectBezier2To", Object=self.Movie2_HintWay, Point1=P1, To=P2, Speed=speed)
        tc.addScope(_scopeTargetPlay)

    def _onAction(self, source, hint):
        source.addFunction(self.Setup)
        source.addScope(self.Check_Action)
        source.addScope(self.scopeAction)

    def _getHintObject(self):
        return

    def _getHintPosition(self, Object):
        return 0, 0

    def destroy_movies_by_name(self):
        # Recovery when another hint still holds the names: frees them for Setup.
        self.Movie2_HintTarget = self.destroy_movie("Movie2_HintTarget")
        self.Movie2_HintWay = self.destroy_movie("Movie2_HintWay")

    def destroy_all_movies(self):
        self.Movie2_HintTarget = self.destroy_own_movie("Movie2_HintTarget", self.Movie2_HintTarget)
        self.Movie2_HintWay = self.destroy_own_movie("Movie2_HintWay", self.Movie2_HintWay)

    def Clean_Full(self):
        self._clearTaskChain()
        self.destroy_all_movies()

        self.Working = False

    def _cleanFullGuard(self, value):
        if value is True:
            return

        self.Clean_Full()

    def _onFinalize(self):
        super(HintActionDefault, self)._onFinalize()

        self.Clean_Full()

    def _onActionComplete(self, isSkip):
        super(HintActionDefault, self)._onActionComplete(isSkip)

        self._onEnd(isSkip)

    def _onEnd(self, someargs=None):
        if self.Working:
            return

        self.Working = True
        self.cancelEndEffect()

        if self.Movie2_HintWay is None:
            self.Clean_Full()

            if self.isEnd() is False:
                self.setEnd()
            return

        self._runEndEffect()

    def _onEndEffect(self, source):
        # The guard releases the effects when the fade chain ends.
        tc_guard = source.makeGuardSource(True, self._cleanFullGuard)
        with tc_guard.addParallelTask(2) as (tc_way, tc_target):
            tc_way.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintWay, To=0.0, Time=self.timer)
            tc_target.addTask("AliasObjectAlphaTo", Object=self.Movie2_HintTarget, To=0.0, Time=self.timer)
            pass
        source.addFunction(self.setEnd)
