from Foundation.ArrowManager import ArrowManager
from Foundation.Task.Task import Task

# DEPRECATED
class TaskInventoryItemDontDrop(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventoryItemDontDrop, self)._onParams(params)
        pass

    def _onRun(self):
        InventoryItem = ArrowManager.getArrowAttach()

        InventoryItemEntity = InventoryItem.getEntity()

        InventoryItemEntity.place()

        return True