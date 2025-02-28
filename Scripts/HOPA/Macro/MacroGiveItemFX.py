from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroGiveItemFX(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 2:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.SocketName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (self.ItemName,))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName,))
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroGiveItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.SocketName)

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=InventoryItem, Object=Object)

        with Quest as tc_quest:
            tc_quest.addTask("AliasGiveItem", Object=Object, SocketName=self.SocketName, ItemName=self.ItemName)
            pass

        source.addDelay(0.1 * 1000)
        pass

    pass
