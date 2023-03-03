from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintInventoryTargetEffectWait(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintInventoryTargetEffectWait, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect",
                       ObjectName="Movie_HintInventoryTarget", Value=self.Position)

        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintInventoryTarget", Wait=True)

        source.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Important=False)
        pass

    pass
