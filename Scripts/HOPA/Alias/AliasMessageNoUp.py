from Foundation.Task.TaskAlias import TaskAlias

class AliasMessageNoUp(TaskAlias):
    def __init__(self):
        super(AliasMessageNoUp, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasMessageNoUp, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(AliasMessageNoUp, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClickEndUp", GroupName="Message", ButtonName="MovieButton_No")
        pass
    pass