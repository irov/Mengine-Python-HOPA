from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintClickSocket(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintClickSocket, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSocketClick", DemonName="Hint", SocketName="Socket_Hint")
        pass
    pass