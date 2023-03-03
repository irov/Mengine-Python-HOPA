from Foundation.GroupManager import GroupManager
from Foundation.Task.Task import Task


class TaskObjectiveFinish(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskObjectiveFinish, self)._onParams(params)

        self.objectiveID = params.get("ObjectiveID")
        pass

    def _onInitialize(self):
        super(TaskObjectiveFinish, self)._onInitialize()
        pass

    def _onRun(self):
        ObjectiveGroup = GroupManager.getGroup("Objectives")
        Demon_Objectives = ObjectiveGroup.getObject("Demon_Objectives")
        Demon_Objectives.delParam("ObjectivesList", self.objectiveID)

        return True
        pass

    pass
