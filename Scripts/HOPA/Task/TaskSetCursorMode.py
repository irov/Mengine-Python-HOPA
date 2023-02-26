from Foundation.ArrowManager import ArrowManager
from Foundation.Task.Task import Task

class TaskSetCursorMode(Task):
    def _onParams(self, params):
        super(TaskSetCursorMode, self)._onParams(params)
        self.cursorMode = params.get("CursorMode")
        pass

    def _onInitialize(self):
        super(TaskSetCursorMode, self)._onInitialize()
        pass

    def _onRun(self):
        ArrowManager.setCursorMode(self.cursorMode)
        return True
        pass