from Foundation.Task.Task import Task

from HOPA.HintManager import HintManager

class TaskHintClearMask(Task):
    def __init__(self):
        super(TaskHintClearMask, self).__init__()
        pass

    def _onRun(self):
        HintManager.clearMask()
        return True
        pass