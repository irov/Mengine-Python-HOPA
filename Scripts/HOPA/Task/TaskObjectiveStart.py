from Foundation.GroupManager import GroupManager
from Foundation.Task.Task import Task


class TaskObjectiveStart(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskObjectiveStart, self)._onParams(params)

        self.objectiveID = params.get("ObjectiveID")
        pass

    def _onInitialize(self):
        super(TaskObjectiveStart, self)._onInitialize()
        pass

    def _onRun(self):
        ObjectiveGroup = GroupManager.getGroup("Objectives")
        Demon_Objectives = ObjectiveGroup.getObject("Demon_Objectives")
        Demon_Objectives.appendParam("ObjectivesList", self.objectiveID)
        return True
        pass

    pass
