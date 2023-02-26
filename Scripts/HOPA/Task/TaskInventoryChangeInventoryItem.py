# from Foundation.Task.Task import Task
#
# from Foundation.ArrowManager import ArrowManager
# from HOPA.ItemManager import ItemManager
# from Foundation.DemonManager import DemonManager
#
# class TaskInventoryChangeInventoryItem(Task):
#    Skiped = True
#
#    def _onParams(self, params):
#        super(TaskInventoryChangeInventoryItem, self)._onParams(params)
#        self.FromName = params.get("FromName")
#        self.ToName = params.get("ToName")
#        self.pickUp = params.get("PickUp", False)
#        pass
#
#    def _onInitialize(self):
#        super(TaskInventoryChangeInventoryItem, self)._onInitialize()
#        pass
#
#    def _onRun(self):
#        arrowItem = ArrowManager.getArrowAttach()
#        if arrowItem is None:
#            Trace.log("TaskInventoryChangeInventoryItem",3,"TaskInventoryRemoveItem._onRun-> arrowItem is None")
#            return False
#            pass
#
#        if self.pickUp is True:
#            item = self.Group.getObject(self.ToName)
#            item.setEnable(False)
#            pass
#
#        arrowItemEntity = arrowItem.getEntity()
#        arrowItemEntity.inInventory()
#
#        arrowItem.setParam("Enable", False)
#        ArrowManager.removeArrowAttach()
#
#        Inventory = DemonManager.get("Inventory")
#        Inventory.changeInventoryItem(self.FromName, self.ToName)
##
#        inventoryItem = ItemManager.getItemInventoryItem(self.ToName)
#        inventoryItem.appendParam("FoundItems", self.ToName)
#
#        return True
#
#        pass
#    pass