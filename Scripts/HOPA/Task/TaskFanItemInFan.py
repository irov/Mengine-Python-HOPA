from Foundation.Task.MixinObjectTemplate import MixinFanItem
from Foundation.Task.Task import Task


class TaskFanItemInFan(MixinFanItem, Task):
    def _onParams(self, params):
        super(TaskFanItemInFan, self)._onParams(params)
        pass

    def _onRun(self):
        FanItemEntity = self.FanItem.getEntity()
        FanItemEntity.inFan()
        return True
        pass

    pass
