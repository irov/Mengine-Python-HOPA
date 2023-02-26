# from Foundation.Task.TaskAlias import TaskAlias
#
# from HOPA.ItemManager import ItemManager
# from Foundation.ArrowManager import ArrowManager
# from Foundation.DefaultManager import DefaultManager
#
# class AliasInventoryAttachInventoryItem(TaskAlias):
#    def _onParams(self, params):
#        super(AliasInventoryAttachInventoryItem, self)._onParams(params)
#
#        self.InventoryItem = params.get("InventoryItem")
#        self.Inventory = params.get("Inventory")
#        pass
#
#    def _onInitialize(self):
#        super(AliasInventoryAttachInventoryItem, self)._onInitialize()
#        pass
#
#    def _onGenerate(self, source):
#        source.addTask("TaskEnable", Object = InventoryItem)
#        source.addTask("TaskArrowAttach", Object = InventoryItem)
#
#        inventoryEntity = self.Inventory.getEntity()
#        id = inventoryEntity.getAddSlotId(self.InventoryItem)
#        with TaskManager.createTaskChain() as tc:
#            tc.addTask("TaskInventorySlotSetItem"
#                , Inventory = self.Inventory
#                , SlotID = id
#                , InventoryItem = self.InventoryItem
#                )
#            pass
#        slot =  self.Inventory.createSlot(self.InventoryItem)
#        source.addTask("TaskAppendParam", Object = self.Inventory, Param = "Slots", Value = slot)
##        source.addTask("TaskNotify", ID = "onInventoryAddInventoryItem", Args = (self.Inventory, self.InventoryItem) )
#        pass
#
#    pass