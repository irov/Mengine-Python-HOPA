from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroUseItemOr(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemsName = values[1:]
        pass

    def _onInitialize(self):
        super(MacroUseItemOr, self)._onInitialize()

        if _DEVELOPMENT is True:
            for ItemName in self.ItemsName:
                if ItemManager.hasItem(ItemName) is False:
                    self.initializeFailed("Item %s not found" % (ItemName))
                    pass

                if ItemManager.hasItemInventoryItem(ItemName) is False:
                    self.initializeFailed("Item %s not have InventoryName" % (ItemName))
                    pass

                if self.hasObject(self.SocketName) is False:
                    self.initializeFailed("MacroUseItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                    pass
                pass
        pass

    def _onGenerate(self, source):
        ItemsCount = len(self.ItemsName)

        with source.addRaceTask(ItemsCount) as tc_races:
            for tc_race, ItemName in zip(tc_races, self.ItemsName):
                InventoryItem = ItemManager.getItemInventoryItem(ItemName)
                tc_race.addTask("TaskSocketPlaceInventoryItem", SocketName=self.SocketName, InventoryItem=InventoryItem, ItemName=ItemName, Taken=False, Pick=False)
                pass
            pass

        source.addListener(Notificator.onInventoryUpdateItem)
        pass

    pass