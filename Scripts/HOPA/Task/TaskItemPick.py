from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.Task import Task

class TaskItemPick(MixinItem, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskItemPick, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(TaskItemPick, self)._onInitialize()
        pass

    def _onRun(self):
        self.Item.setParams(Enable=False)

        return True
        pass
    pass