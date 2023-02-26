from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintReadyMovieStop(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyMovieStop, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()
        HintGroup = self.Hint.getGroup()

        source.addTask("TaskMovie2Stop", Group=HintGroup, Movie2Name="Movie2_Ready")
        source.addTask("TaskEnable", Group=HintGroup, ObjectName="Movie2_Ready", Value=False)
        if HintGroup.hasObject("Movie2_Ready_Effect"):
            source.addTask("TaskEnable", Group=HintGroup, ObjectName="Movie2_Ready_Effect", Value=False)
            pass
        pass
    pass