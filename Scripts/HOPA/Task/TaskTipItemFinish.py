from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task

class TaskTipItemFinish(MixinGroup, Task):
    Skiped = True

    def _onRun(self):
        Demon_TipItem = self.Group.getObject("Demon_TipItem")
        Demon_TipEntity = self.Demon_TipItem.getEntity()
        Demon_TipEntity.tipHide()

        self.addObserverFilter(Notificator.onTipItemFinish, self._onTipHideComplete, Demon_TipItem)

        return False
        pass

    def _onTipHideComplete(self, tip):
        return True
        pass
    pass