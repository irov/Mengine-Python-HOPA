from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskBonusItemCollect(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskBonusItemCollect, self)._onParams(params)

        self.BonusItemName = params.get("BonusItemName")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onBonusItemCollect, self._onBonusItemCollect)

        return False
        pass

    def _onBonusItemCollect(self, name):
        if self.BonusItemName != name:
            return False
            pass

        return True
        pass
    pass