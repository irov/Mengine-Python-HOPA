from Foundation.Task.MixinObjectTemplate import MixinFanItem
from Foundation.Task.Task import Task

class TaskFanItemInNone(MixinFanItem, Task):
    Skiped = True
    def _onParams(self, params):
        super(TaskFanItemInNone, self)._onParams(params)
        pass

    def _onRun(self):
        FanItemEntity = self.FanItem.getEntity()
        FanItemEntity.inNone()
        return True
        pass
    pass