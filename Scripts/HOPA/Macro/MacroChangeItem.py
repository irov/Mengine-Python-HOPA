from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroChangeItem(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 3:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.SocketName = values[0]
        self.inItemName = values[1]
        self.outItemName = values[2]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.inItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (self.inItemName))
                pass

            if ItemManager.hasItem(self.outItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (self.outItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.inItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.inItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.outItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.outItemName))
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroGiveItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.SocketName)

        def __inItem(item):
            return item == inInventoryItem
            pass

        inInventoryItem = ItemManager.getItemInventoryItem(self.inItemName)
        outInventoryItem = ItemManager.getItemInventoryItem(self.outItemName)
        Inventory = DemonManager.getDemon("Inventory")

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=inInventoryItem, Object=Object)

        with Quest as tc_quest:
            tc_quest.addTask("AliasGiveItem", Object=Object, SocketName=self.SocketName, ItemName=self.inItemName,
                             SceneName=self.SceneName, Group_Name=self.GroupName)
            pass

        source.addListener(Notificator.onInventoryUpdateItem)

        source.addTask("TaskInventorySlotAddInventoryItem", Inventory=Inventory, InventoryItem=outInventoryItem)
        source.addTask("TaskInventoryAddItem", Inventory=Inventory, ItemName=self.outItemName, ItemHide=True)
        source.addTask("TaskArrowAttachInventoryItem", Inventory=Inventory, InventoryItem=outInventoryItem)
        pass

    pass
