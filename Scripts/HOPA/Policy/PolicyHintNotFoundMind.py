from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintNotFoundMind(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintNotFoundMind, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("AliasMindPlay", MindID="ID_HINTNOTFOUND")
        pass

    pass
