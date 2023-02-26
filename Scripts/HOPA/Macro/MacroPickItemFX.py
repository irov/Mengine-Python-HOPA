from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroPickItemFX(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        pass

    def _onInitialize(self):
        FinderType, self.Item = self.findObject(self.ItemName)

        if _DEVELOPMENT is True:
            if self.Item is None:
                self.initializeFailed("Not found current item %s with this group %s in ItemManager" % (self.ItemName, self.GroupName))
                pass

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))
                pass

            if ItemManager.hasItemObject(self.ItemName) is False:
                self.initializeFailed("Item %s not have ObjectName" % (self.ItemName,))
                pass

            if self.hasObject(self.Item.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.Item.name, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ItemObject = ItemManager.getItemObject(self.ItemName)
        ItemObjectName = ItemObject.getName()

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName, ItemName=ItemObjectName)

        with Quest as tc_quest:
            tc_quest.addTask("AliasFindItem", SceneName=self.SceneName, ItemName=self.ItemName)

            if ItemManager.hasItemInventoryItem(self.ItemName) is True:
                Inventory = DemonManager.getDemon("Inventory")

                tc_quest.addTask("AliasInventoryAddInventoryItemFX", Inventory=Inventory, ItemName=self.ItemName, EffectPolicy="ActionPickItem")
                pass
            pass
        pass

    pass