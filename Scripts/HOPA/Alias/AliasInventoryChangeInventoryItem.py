# from Foundation.Task.TaskAlias import TaskAlias
# from HOPA.ItemManager import ItemManager
#
# class AliasInventoryChangeInventoryItem(TaskAlias):
#    def _onParams(self, params):
#        super(AliasInventoryChangeInventoryItem, self)._onParams(params)
#        self.fromName = params.get("FromName")
#        self.toName   = params.get("ToName")
#        self.Inventory  = params.get("Inventory")
#        pass
#
#    def _onGenerate(self, source):
#        ### look:
#        fromInventoryItem = ItemManager.getItemInventoryItem(self.fromName)
#        toInventoryItem = ItemManager.getItemInventoryItem(self.toName)
#        SlotCount = self.Inventory.getParam("SlotCount")
#
#        InventoryItemReturnIndex = self.Inventory.getSlotIndex(fromInventoryItem)
#
#        slot = self.Inventory.getSlot(fromInventoryItem)
#        slot.item = toInventoryItem
#        toInventoryItemEntity = toInventoryItem.getEntity()
#        sprite = toInventoryItemEntity.getSprite()
#        size = sprite.getImageSize()
#
#        source.addTask( "TaskArrowAttach", Object = toInventoryItem )
#        source.addTask( "TaskObjectSetPosition", Object = toInventoryItem,
#                        Value = (-size.x/2, -size.y/2))
#        source.addTask( "TaskChangeParam"
#                      , Object = self.Inventory
#                      , Param = "Slots"
#                      , KeyID = InventoryItemReturnIndex
#                      , Value = slot)
#
#        source.addTask("AliasEffectInventoryReturnInventoryItem" )
#        source.addTask("TaskRemoveArrowAttach")
#
#        ReturnSlotIndex = int(InventoryItemReturnIndex / SlotCount) * SlotCount
#        SetSlotIndex = InventoryItemReturnIndex - ReturnSlotIndex
##        slotId = InventoryItemReturnIndex - CurrentSlotIndex
#        source.addTask("TaskInventorySlotSetItem"
#                     , Inventory = self.Inventory
#                     , SlotID = SetSlotIndex
#                     , InventoryItem = toInventoryItem)
#        source.addTask("TaskNotify", ID = "onInventoryReturnInventoryItem", Args = (self.Inventory, toInventoryItem))
##        source.addTask( "TaskInventorySlotSetItem", InventoryItemName =  toInventoryItemName, Inventory = self.Inventory, SlotID = slotId)
#        source.addTask( "TaskAppendParam", Object = toInventoryItem, Param = "FoundItems", Value = self.toName)
#        pass
#
#    pass
