from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintTargetDummy(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetDummy, self)._onParams(params)
        self.Position = params.get("Position", None)
        self.Point = params.get("Point", None)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskDummy")
        pass

    pass
