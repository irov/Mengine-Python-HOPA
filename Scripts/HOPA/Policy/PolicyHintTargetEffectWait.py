from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintTargetEffectWait(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetEffectWait, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie2_HintTarget", Value=self.Position)
        source.addTask("TaskMovie2Play", GroupName="HintEffect", Movie2Name="Movie2_HintTarget", Wait=True, Loop=False)  # Loop=True

        source.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Important=False)
        pass
    pass