from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintInventoryTargetLoopEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintInventoryTargetLoopEffect, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintInventoryTargetLoop", Value=self.Position)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintInventoryTargetLoop", Loop=True, Wait=False)

        source.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Important=False)
        pass
    pass