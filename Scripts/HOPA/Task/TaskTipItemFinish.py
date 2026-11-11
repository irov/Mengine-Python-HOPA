from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task


class TaskTipItemFinish(MixinGroup, Task):
    Skiped = True

    def _onRun(self):
        Demon_TipItem = self.Group.getObject("Demon_TipItem")
        Demon_TipEntity = Demon_TipItem.getEntity()
        Demon_TipEntity.tipHide()

        return True
        pass

    pass
