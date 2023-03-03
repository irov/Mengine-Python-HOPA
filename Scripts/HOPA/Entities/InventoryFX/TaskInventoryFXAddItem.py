from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskInventoryFXAddItem(MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventoryFXAddItem, self)._onParams(params)
        self.InventoryItem = params.get("InventoryItem")
        self.ItemName = params.get("ItemName")
        pass

    def _onRun(self):
        def __thisItem(action, inventory, invItem, itemName):
            if invItem is not self.InventoryItem:
                return False
                pass

            if itemName is not self.ItemName:
                return False
                pass

            return True
            pass

        self.addObserver(Notificator.onInventoryFXActionEnd, __thisItem)

        return False
        pass

    pass
