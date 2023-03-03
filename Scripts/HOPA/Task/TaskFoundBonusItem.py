from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.Task import Task
from HOPA.BonusItemManager import BonusItemManager


class TaskFoundBonusItem(MixinItem, Task):
    def _onParams(self, params):
        super(TaskFoundBonusItem, self)._onParams(params)

        self.BonusItemName = params.get("BonusItemName")

        self.BonusItem = None
        pass

    def _onInitialize(self):
        super(TaskFoundBonusItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if BonusItemManager.hasItem(self.BonusItemName) is False:
                self.initializeFailed("BonusItem %s not found" % (self.BonusItemName))
                pass
            pass

        self.BonusItem = BonusItemManager.getItemStoreObject(self.BonusItemName)
        pass

    def _onRun(self):
        self.BonusItem.appendParam("FoundItems", self.Item)

        return True
        pass

    pass
