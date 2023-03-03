from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskInventoryScrolling(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskInventoryScrolling, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Coordination = params.get("Coordination")
        self.ExceptSlots = params.get("ExceptSlots", [])
        pass

    def _onRun(self):
        if self.Inventory.isActive() is False:
            return True
            pass

        Entity = self.Inventory.getEntity()
        Entity.scrollingSlots(self.Coordination, self.ExceptSlots)

        def __onScrollingEndFilter(inventory):
            return True
            pass

        self.addObserverFilter(Notificator.onInventoryScrolling, __onScrollingEndFilter, self.Inventory)

        return False
        pass

    pass
