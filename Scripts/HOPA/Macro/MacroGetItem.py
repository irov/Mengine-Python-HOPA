from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.PopUpItemManager import PopUpItemManager

class MacroGetItem(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if PopUpItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("PopUpItem %s not found" % (self.ItemName))
                pass

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        # print "MacroGetItem"

        Quest = self.addQuest(source, "GetItem", SceneName=self.SceneName, GroupName=self.GroupName)

        with Quest as tc_quest:
            tc_quest.addTask("AliasInventoryGetInventoryItem", ItemName=self.ItemName)
        pass
    pass