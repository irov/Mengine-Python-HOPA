from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.BonusItemManager import BonusItemManager


class TaskEnableBonusItem(MixinObserver, TaskAlias):
    def _onParams(self, params):
        super(TaskEnableBonusItem, self)._onParams(params)

        self.Value = params.get("Value")
        pass

    def _onGenerate(self, source):
        Items = BonusItemManager.getBonusItem()
        for item in Items:
            source.addTask("TaskInteractive", Object=item, Value=self.Value)
            pass
        pass

    pass
