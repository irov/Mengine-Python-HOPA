from Foundation.Task.TaskAlias import TaskAlias


class PolicyDialogStaticText(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogStaticText, self)._onParams(params)

        self.ObjectText = params.get("ObjectText")
        self.TextID = params.get("TextID")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSetParam", Object=self.ObjectText, Param="TextID", Value=self.TextID)
        source.addTask("TaskEnable", Object=self.ObjectText, Value=True)
        pass

    pass
