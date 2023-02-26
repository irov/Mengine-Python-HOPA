from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskTipFinish(MixinGroup, MixinObserver, Task):
    Skiped = True

    def _onRun(self):
        Demon_Tip = self.Group.getObject("Demon_Tip")
        Demon_TipEntity = Demon_Tip.getEntity()
        Demon_TipEntity.tipHide()

        self.addObserverFilter(Notificator.onTipFinish, self._onTipHideComplete, Demon_Tip)

        return False
        pass

    def _onTipHideComplete(self, tip):
        return True
        pass
    pass