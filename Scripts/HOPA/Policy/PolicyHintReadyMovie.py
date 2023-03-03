from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintReadyMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyMovie, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()

        MovieGroup = self.Hint.getGroup()

        source.addTask("TaskEnable", Group=MovieGroup, ObjectName="Movie2_Reload", Value=False)
        source.addTask("TaskEnable", Group=MovieGroup, ObjectName="Movie2_Ready")
        source.addTask("TaskMovie2Play", Group=MovieGroup, Movie2Name="Movie2_Ready", Loop=True, Wait=False)
        pass

    pass
