from Foundation.DemonManager import DemonManager
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
        pass

    def _onGenerate(self, source):
        ItemsCount = len(self.ItemsName)
        FinderType, Object = self.findObject(self.SocketName)
        Inventory = DemonManager.getDemon("Inventory")

        Quest = self.addQuest(source, "GiveItemOr", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, ItemNames=self.ItemsName, Object=Object)

        with Quest as tc_quest:
            with tc_quest.addRaceTask(ItemsCount) as tc_races:
                for tc_race, ItemName in zip(tc_races, self.ItemsName):
                    InventoryItem = ItemManager.getItemInventoryItem(ItemName)
                    tc_race.addTask("TaskSocketPlaceInventoryItem", SocketName=self.SocketName,
                                    InventoryItem=InventoryItem, ItemName=ItemName, Taken=False, Pick=False)
                    pass
                pass
            pass

        source.addListener(Notificator.onInventoryUpdateItem)
        pass

    pass
