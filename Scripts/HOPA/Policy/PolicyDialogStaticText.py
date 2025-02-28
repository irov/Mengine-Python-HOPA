from Foundation.Task.TaskAlias import TaskAlias


class PolicyDialogStaticText(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogStaticText, self)._onParams(params)

        self.ObjectText = params.get("ObjectText")
        self.TextID = params.get("TextID")
        pass

    def _onGenerate(self, source):
        source.addParam(self.ObjectText, "TextID", self.TextID)
        source.addEnable(self.ObjectText)
        pass

    pass
