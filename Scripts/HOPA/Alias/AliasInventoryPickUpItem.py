## To change this template, choose Tools | Templates
## and open the template in the editor.
#
# from Foundation.Task.TaskAlias import TaskAlias
# from Foundation.Task.MixinObjectTemplate import MixinItem
# from HOPA.ItemManager import ItemManager
# from Foundation.DemonManager import DemonManager
#
# class AliasInventoryPickUpItem(MixinItem, TaskAlias):
#    def _onParams(self, params):
#        super(AliasInventoryPickUpItem, self)._onParams(params)
#        self.ItemName = params.get("ItemName")
#        self.Inventory = DemonManager.getDemon("Inventory")
#        pass
#
#    def _onGenerate(self, source):
##        objectItem = ItemManager.getItemObject(self.ItemName)
##        source.addTask( "AliasEffectBeforeInventoryAddItem", Item = objectItem )
##        source.addTask( "TaskStateMutex", ID = "StateAddItem", From = False, To = True)
##        source.addTask( "TaskEffectInventoryAddItem", ItemName = self.ItemName, Front = False)
##        source.addTask( "TaskEffectInventorySlotAdd", ItemName = self.ItemName)
##        source.addTask( "AliasInventoryAddInventoryItem", Inventory = self.Inventory, ItemName = self.ItemName)
##        source.addTask( "TaskStateChange", ID = "StateAddItem", Value = False)
#        pass
#
#    pass
