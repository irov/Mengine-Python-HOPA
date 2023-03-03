from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.PopUpItemManager import PopUpItemManager


class MacroCombine(MacroCommand):
    def _onValues(self, values):
        self.FirstItemName = values[0]
        self.SecondItemName = values[1]

        self.CombineItemNames = [(self.FirstItemName, self.SecondItemName), (self.SecondItemName, self.FirstItemName)]

        self.GetItemName = values[2] if len(values) == 3 else None
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            CombineItemNamesCount = len(self.CombineItemNames)

            if CombineItemNamesCount == 0:
                self.initializeFailed("CombineInventoryItem is empty")
                pass

            if ItemManager.hasItem(self.FirstItemName) is False:
                self.initializeFailed("Item %s not found" % (self.FirstItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.FirstItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.FirstItemName))
                pass

            if ItemManager.hasItem(self.SecondItemName) is False:
                self.initializeFailed("Item %s not found" % (self.SecondItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.SecondItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.SecondItemName))
                pass

            if self.GetItemName is not None:
                if ItemManager.hasItem(self.GetItemName) is False:
                    self.initializeFailed("GetItem %s not found" % (self.GetItemName))
                    pass

                if ItemManager.hasItemInventoryItem(self.GetItemName) is False:
                    self.initializeFailed("GetItem %s not have InventoryName" % (self.GetItemName))
                    pass

                if PopUpItemManager.hasItem(self.GetItemName) is False:
                    self.initializeFailed("ItemPopUp %s not found" % (self.GetItemName))

    def _onGenerate(self, source):
        Inventory = DemonManager.getDemon("Inventory")
        CombineItemNamesCount = len(self.CombineItemNames)
        AttachInventoryItem = ItemManager.getItemInventoryItem(self.FirstItemName)
        SlotInventoryItem = ItemManager.getItemInventoryItem(self.SecondItemName)

        Quest = self.addQuest(source, "Combine", GroupName=self.GroupName, Inventory=Inventory,
                              AttachInventoryItem=AttachInventoryItem, SlotInventoryItem=SlotInventoryItem)

        with Quest as tc_quest:
            with tc_quest.addRaceTask(CombineItemNamesCount) as tcs:
                for tci, CombineNames in zip(tcs, self.CombineItemNames):
                    AttachInventoryItem = ItemManager.getItemInventoryItem(CombineNames[0])
                    SlotInventoryItem = ItemManager.getItemInventoryItem(CombineNames[1])

                    tci.addTask("AliasInventoryCombineInventoryItem", Inventory=Inventory,
                                AttachInventoryItem=AttachInventoryItem, SlotInventoryItem=SlotInventoryItem)

        if self.GetItemName is not None:
            source.addTask("AliasInventoryGetInventoryItem", ItemName=self.GetItemName)
