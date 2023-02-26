from Foundation.Task.TaskAlias import TaskAlias

class PolicyDummy(TaskAlias):
    def _onGenerate(self, source):
        source.addTask("TaskDummy")
        pass
    pass