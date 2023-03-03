from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskHOGFittingItemUse(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskHOGFittingItemUse, self)._onParams(params)
        self.ItemObject = params.get("ItemObject")
        self.ItemUseObject = params.get("ItemUseObject")
        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(TaskHOGFittingItemUse, self)._onInitialize()
        pass

    def _onRun(self):
        self.ItemObject.setInteractive(True)
        self.addObserverFilter(Notificator.onItemClick, self._onItemFindFilter, self.ItemObject)
        return False
        pass

    def _onItemFindFilter(self, item):
        if ArrowManager.emptyArrowAttach() is True:
            return False
            pass

        attach = ArrowManager.getArrowAttach()

        if attach is not self.ItemUseObject:
            return False
            pass

        inv_Ent = self.Inventory.getEntity()
        inv_Ent.ItemIsValideUse = True
        # Visual change cursor
        self.ItemObject.setInteractive(False)
        return True
        pass

    def _onFinally(self):
        super(TaskHOGFittingItemUse, self)._onFinally()

        self.ItemObject.setInteractive(False)
        pass

    pass
