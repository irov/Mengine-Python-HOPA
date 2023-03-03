from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintEmptyDefault(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintEmptyDefault, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSoundEffect", SoundName="HintReady", Important=False)
        pass

    pass
