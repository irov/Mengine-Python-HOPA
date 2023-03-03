from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroWaitItem(MacroCommand):
    def _onValues(self, values):
        self.ItemNameList = values

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            wrong_names = []

            for itemName in self.ItemNameList:
                if ItemManager.hasItem(itemName) is False:
                    wrong_names.append(itemName)

            if len(wrong_names) > 0:
                self.initializeFailed("MacroWaitItem: wrong item names {} or not registered in InventoryItems.xlsx".format(wrong_names))

    def __hasItem(self, InventoryItem):
        Inventory = DemonManager.getDemon("Inventory")
        return Inventory.hasInventoryItem(InventoryItem)

    def __waitItem(self, source, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        if self.__hasItem(InventoryItem) is True:
            if InventoryItem.checkCount() is False:
                source.addListener(Notificator.onInventoryItemCountComplete, Filter=lambda item: item == InventoryItem)
            return

        ItemObject = None
        if ItemManager.hasItemObject(itemName):
            ItemObject = ItemManager.getItemObject(itemName)

        with source.addRaceTask(3) as (race_0, race_1, race_2):
            race_0.addListener(Notificator.onItemPicked, Filter=lambda item: item == ItemObject)
            race_1.addListener(Notificator.onInventoryAddItem, Filter=lambda inv, item: item == InventoryItem)

            race_2.addDelay(1000)  # If item picked but notify not reached when macro started
            with race_2.addIfTask(self.__hasItem, InventoryItem) as (true, false):
                true.addDummy()  # race end
                false.addBlock()  # wait race_0, race_1

        with source.addIfTask(InventoryItem.checkCount) as (full, not_full):
            not_full.addListener(Notificator.onInventoryItemCountComplete, Filter=lambda item: item == InventoryItem)

    def _onGenerate(self, source):
        for itemName, _source in source.addParallelTaskList(self.ItemNameList):
            if ItemManager.hasItemInventoryItem(itemName) is True:
                _source.addScope(self.__waitItem, itemName)
            else:
                _source.addDummy()
