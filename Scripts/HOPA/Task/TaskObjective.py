from Foundation.GroupManager import GroupManager
from Foundation.Task.Task import Task

class TaskObjective(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskObjective, self)._onParams(params)

        self.ObjectiveID = params.get("ObjectiveID")
        pass

    def _onInitialize(self):
        super(TaskObjective, self)._onInitialize()
        pass

    def _onRun(self):
        ObjectiveGroup = GroupManager.getGroup("Objective")
        Demon_Objective = ObjectiveGroup.getObject("Demon_Objective")

        Demon_Objective.setParam("ObjectiveID", self.ObjectiveID)

        return True
        pass
    pass