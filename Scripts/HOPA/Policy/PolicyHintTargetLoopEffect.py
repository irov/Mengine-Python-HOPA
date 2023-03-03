from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintTargetLoopEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetLoopEffect, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintTargetLoop",
                       Value=self.Position)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintTargetLoop", Loop=True, Wait=False)
        pass

    pass
