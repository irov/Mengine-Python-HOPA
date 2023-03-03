from Foundation.Task.MixinObjectTemplate import MixinFanItem
from Foundation.Task.Task import Task


class TaskFanItemInHand(MixinFanItem, Task):
    def _onParams(self, params):
        super(TaskFanItemInHand, self)._onParams(params)
        pass

    def _onRun(self):
        FanItemEntity = self.FanItem.getEntity()
        FanItemEntity.inHand()
        return True
        pass

    pass
