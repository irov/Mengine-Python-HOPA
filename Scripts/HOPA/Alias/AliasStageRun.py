from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias
from Foundation.TaskManager import TaskManager

class AliasStageRun(TaskAlias):
    def __init__(self):
        super(AliasStageRun, self).__init__()
        self.fadeInAlpha = 1.0
        self.fadeInTime = 0.15 * 1000  # speed fix
        pass

    def _onParams(self, params):
        super(AliasStageRun, self)._onParams(params)

        self.StageName = params.get("StageName")
        self.Intro = params.get("Intro", False)
        pass

    def _onGenerate(self, source1):
        with TaskManager.createTaskChain() as source:
            source.addTask("TaskTransitionUnblock", IsGameScene=True)
            source.addTask("TaskTransitionBlock", Value=True, IsGameScene=True)

            if self.Intro is False:
                with GuardBlockInput(source) as guard_source:
                    guard_source.addTask("AliasFadeIn", To=self.fadeInAlpha, Time=self.fadeInTime)
                    guard_source.addTask("TaskSceneLeaving")
                    pass
                pass

            source.addTask("TaskTransitionBlock", Value=False, IsGameScene=True)

            source.addTask("TaskStageRun", StageName=self.StageName)
            pass
        pass
    pass