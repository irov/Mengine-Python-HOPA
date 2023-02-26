from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.Task import Task

class TaskItemAutoClick(MixinItem, Task):
    def _onParams(self, params):
        super(TaskItemAutoClick, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Item.setEnable(True)
            pass

        ItemEntity = self.Item.getEntity()
        ItemEntity.clickItem()

        return True
        pass

    def _onFinally(self):
        super(TaskItemAutoClick, self)._onFinally()

        if self.AutoEnable is True:
            self.Item.setInteractive(False)
            pass
        pass
    pass