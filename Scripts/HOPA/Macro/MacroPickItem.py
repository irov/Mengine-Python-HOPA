from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroPickItem(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]

    def _onInitialize(self):
        FinderType, self.Item = self.findObject(self.ItemName)

        if _DEVELOPMENT is True:
            if self.Item is None:
                self.initializeFailed("Not found current item %s with this group %s in ItemManager" % (self.ItemName, self.GroupName))

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % self.ItemName)

            if ItemManager.hasItemObject(self.ItemName) is False:
                self.initializeFailed("Item %s not have ObjectName" % self.ItemName)

            if self.hasObject(self.Item.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.Item.name, self.GroupName))

    def _onGenerate(self, source):
        ItemObject = ItemManager.getItemObject(self.ItemName)
        ItemObjectName = ItemObject.getName()

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName,
                              ItemName=ItemObjectName)
        if ItemManager.hasItemInventoryItem(self.ItemName) is True:
            Inventory = DemonManager.getDemon("Inventory")

            with Quest as tc_quest:
                tc_quest.addTask("AliasFindItem", Inventory=Inventory, SceneName=self.SceneName, ItemName=self.ItemName)
            with source.addFork() as tc_fork:
                tc_fork.addFunction(Inventory.BlockButtons)
                tc_fork.addTask("AliasInventoryAddInventoryItem", Inventory=Inventory, ItemName=self.ItemName)
                tc_fork.addFunction(Inventory.UnBlockButtons)
