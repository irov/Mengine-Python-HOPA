from Foundation.Task.TaskAlias import TaskAlias

class PolicyTransitionBack(TaskAlias):
    def _onParams(self, params):
        super(PolicyTransitionBack, self)._onParams(params)
        self.PositionTo = params.get("Position")
        self.effect = params.get("Effect")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskMoviePlay", Movie=self.effect, Wait=True, Loop=True, AutoEnable=True)

        pass
    pass