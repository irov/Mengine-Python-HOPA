from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task
from Foundation.TaskManager import TaskManager


class PolicyInteractionShiftCollect(MixinGroup, Task):
    Skiped = False

    def _onParams(self, params):
        super(PolicyInteractionShiftCollect, self)._onParams(params)

        self.Collects = params.get("Collects")
        pass

    def _onRun(self):
        if self._test() is True:
            return True
            pass

        SceneName = SceneManager.getCurrentSceneName()

        for index, collect in enumerate(self.Collects):
            with TaskManager.createTaskChain(Name="ShiftCollect_%s" % (index), Group=self.Group, Repeat=True) as tc:
                tc.addTask("AliasObjectClick", ObjectName=collect["InteractionName"], IsQuest=True, SceneName=SceneName)
                tc.addTask("TaskShiftNext", ShiftName=collect["ShiftName"])
                tc.addCallback(self._onCollectTest)
                pass
            pass

        return False
        pass

    def _onFinally(self):
        for index, collect in enumerate(self.Collects):
            TaskManager.cancelTaskChain("ShiftCollect_%s" % (index))
            pass
        pass

    def _onCollectTest(self, isSkip, cb):
        if self._test() is False:
            cb(isSkip)
            return
            pass

        self.complete()

        cb(isSkip)
        pass

    def _test(self):
        for collect in self.Collects:
            ShiftName = collect["ShiftName"]
            Shift = self.Group.getObject(ShiftName)

            State = Shift.getParam("Shift")

            WaitState = collect["State"]
            if State != WaitState:
                return False
                pass
            pass

        return True
        pass

    def _onSkip(self):
        for collect in self.Collects:
            ShiftName = collect["ShiftName"]
            Shift = self.Group.getObject(ShiftName)

            WaitState = collect["State"]
            Shift.setShift(WaitState)
            pass
        pass

    pass
