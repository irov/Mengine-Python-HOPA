from Foundation.Task.TaskAlias import TaskAlias

class AliasMessageYesUp(TaskAlias):
    def __init__(self):
        super(AliasMessageYesUp, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasMessageYesUp, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(AliasMessageYesUp, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClickEndUp", GroupName="Message", ButtonName="MovieButton_Yes")
        pass
    pass