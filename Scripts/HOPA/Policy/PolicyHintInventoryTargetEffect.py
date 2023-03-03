from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintInventoryTargetEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintInventoryTargetEffect, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect",
                       ObjectName="Movie2_HintInventoryTarget", Value=self.Position)

        source.addTask("TaskMovie2Play", GroupName="HintEffect",
                       Movie2Name="Movie2_HintInventoryTarget", Wait=True, Loop=False)

        source.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Important=False)
        pass

    pass
