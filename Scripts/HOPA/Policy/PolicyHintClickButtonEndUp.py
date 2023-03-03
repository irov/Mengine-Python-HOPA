from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintClickButtonEndUp(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintClickButtonEndUp, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClickEndUp", DemonName="Hint", ButtonName="Button_Hint")
        pass

    pass
