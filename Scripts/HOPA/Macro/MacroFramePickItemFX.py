from Foundation.GroupManager import GroupManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroFramePickItemFX(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        pass

    def _onInitialize(self):
        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        self.Button = Demon.getObject("Button_Ok")

        FinderType, self.Item = self.findObject(self.ItemName)

        if _DEVELOPMENT is True:
            if self.Item is None:
                self.initializeFailed("Not found current item %s with this group %s in ItemManager" % (self.ItemName, self.GroupName))
                pass

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName,))
                pass

            if ItemManager.hasItemObject(self.ItemName) is False:
                self.initializeFilead("Item %s not have ObjectName" % (self.ItemName,))
                pass

            if self.hasObject(self.Item.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.Item.name, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ItemObject = ItemManager.getItemObject(self.ItemName)
        ItemObjectName = ItemObject.getName()

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName,
                              ItemName=ItemObjectName)

        with Quest as tc_quest:
            tc_quest.addTask("AliasFindItem", SceneName=self.SceneName, ItemName=self.ItemName)
            pass

        if ItemManager.hasItemInventoryItem(self.ItemName) is True:
            Quest = self.addQuest(source, "GetItem", SceneName=self.SceneName, GroupName=self.GroupName,
                                  Object=self.Button)

            with Quest as tc_quest:
                tc_quest.addTask("AliasInventoryGetInventoryItem", ItemName=self.ItemName)
