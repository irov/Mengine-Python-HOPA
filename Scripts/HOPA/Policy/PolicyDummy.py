from Foundation.Task.TaskAlias import TaskAlias


class PolicyDummy(TaskAlias):
    def _onGenerate(self, source):
        source.addDummy()
        pass

    pass
