from Foundation.Task.Task import Task

from HOPA.HintManager import HintManager

class TaskHintSetMask(Task):
    def __init__(self):
        super(TaskHintSetMask, self).__init__()
        self.Mask = []
        pass

    def _onParams(self, params):
        super(TaskHintSetMask, self)._onParams(params)
        self.Mask = params.get("Mask")
        pass

    def _onRun(self):
        HintManager.setMask(self.Mask)
        return True
        pass