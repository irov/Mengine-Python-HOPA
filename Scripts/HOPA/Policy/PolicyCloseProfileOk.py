from Foundation.Task.TaskAlias import TaskAlias

class PolicyCloseProfileOk(TaskAlias):
    def _onParams(self, params):
        super(PolicyCloseProfileOk, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClick", GroupName="Profile", ButtonName="Button_Ok")
        pass
    pass