from Event import Event
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task
from Foundation.TaskManager import TaskManager
from HOPA.QuestManager import QuestManager

class PolicySocketShiftCollect(MixinGroup, Task):
    Skiped = False

    def _onParams(self, params):
        super(PolicySocketShiftCollect, self)._onParams(params)

        self.Collects = params.get("Collects")
        self.Index = params.get("Index")
        self.Name = None
        self.EventComplete = None

    def _onCheck(self):
        return not self._test()

    def _onRun(self):
        self.Name = "ShiftCollect_%s_%d" % (self.Group.getName(), self.Index)

        self.EventComplete = Event(self.Name + "CompleteEvent")

        SceneName = SceneManager.getCurrentSceneName()

        for collect_index, collect in enumerate(self.Collects):
            Object = self.Group.getObject(collect["InteractionName"])

            Quest = QuestManager.createLocalQuest("ShiftCollect", SceneName=SceneName, GroupName=self.Group.getName(), Collects=self.Collects, CollectIndex=collect_index)

            with TaskManager.createTaskChain(Name=self.Name + str(collect_index), Group=self.Group) as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    with tc_quest.addRepeatTask() as (tc_repeat, tc_until):
                        tc_repeat.addTask("AliasObjectClick", ObjectName=collect["InteractionName"], IsQuest=False, SceneName=SceneName)

                        tc_repeat.addTask("TaskShiftNext", ShiftName=collect["ShiftName"])

                        tc_repeat.addNotify(Notificator.onShiftNext, Object)
                        tc_repeat.addCallback(self._checkCollectsComplete)

                        tc_until.addEvent(self.EventComplete)

        ''' Skip shift collect '''
        with TaskManager.createTaskChain(Name=self.Name + 'Cancel') as tc:
            tc.addListener(Notificator.onShiftCollectSkip)
            tc.addFunction(self.EventComplete)
            tc.addFunction(self.complete)

        return False

    def _onFinally(self):
        super(PolicySocketShiftCollect, self)._onFinally()

        self.EventComplete = None

    def _checkCollectsComplete(self, isSkip, cb):
        if self._test() is False:
            cb(isSkip)
            return

        self.EventComplete()
        self.complete()

        cb(isSkip)

    def _test(self):
        for collect in self.Collects:
            ShiftName = collect["ShiftName"]
            Shift = self.Group.getObject(ShiftName)

            State = Shift.getShift()

            WaitState = collect["State"]
            if State != WaitState:
                return False

        return True