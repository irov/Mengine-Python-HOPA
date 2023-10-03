from HOPA.CursorManager import CursorManager
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
        CursorManager.setCursorMode(self.cursorMode)
        return True
        pass
