from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TipManager import TipManager

class MacroGiveItemTip(MacroCommand):

    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 3:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))

        self.SocketName = values[0]
        self.ItemName = values[1]
        self.TipName = values[2]

        self.Inventory = None
        self.InventoryItemObject = None
        self.SocketObject = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % self.ItemName)

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % self.ItemName)

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroGiveItem not found Object %s in group %s" % (self.SocketName, self.GroupName))

            if TipManager.hasTip(self.TipName) is False:
                self.initializeFailed("Tip %s not found" % self.TipName)

        FinderType, Object = self.findObject(self.SocketName)

        self.SocketObject = Object
        self.InventoryItemObject = ItemManager.getItemInventoryItem(self.ItemName)
        self.Inventory = DemonManager.getDemon("Inventory")

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=self.Inventory, GroupName=self.GroupName, InventoryItem=self.InventoryItemObject, Object=self.SocketObject)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, self.SocketObject, self.TipName)
            tc_quest.addTask("AliasGiveItem", Object=self.SocketObject, SocketName=self.SocketName, ItemName=self.ItemName, TipName=self.TipName)
            tc_quest.addNotify(Notificator.onTipRemoveWithoutParagraphs, self.TipName)

        source.addListener(Notificator.onInventoryUpdateItem)