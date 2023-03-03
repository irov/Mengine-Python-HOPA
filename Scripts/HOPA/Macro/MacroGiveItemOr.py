from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroGiveItemOr(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemsName = values[1:]
        pass

    def _onInitialize(self):
        super(MacroGiveItemOr, self)._onInitialize()

        if _DEVELOPMENT is True:
            for ItemName in self.ItemsName:
                if ItemManager.hasItem(ItemName) is False:
                    self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (ItemName))
                    pass

                if ItemManager.hasItemInventoryItem(ItemName) is False:
                    self.initializeFailed("Item %s not have InventoryName" % (ItemName))
                    pass
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroGiveItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.SocketName)
        ItemsCount = len(self.ItemsName)
        Inventory = DemonManager.getDemon("Inventory")

        Quest = self.addQuest(source, "GiveItemOr", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, ItemNames=self.ItemsName, Object=Object)

        with Quest as tc_quest:
            with tc_quest.addRaceTask(ItemsCount) as tc_races:
                for tc_race, ItemName in zip(tc_races, self.ItemsName):
                    tc_race.addTask("AliasGiveItem", Object=Object, SocketName=self.SocketName, ItemName=ItemName,
                                    SceneName=self.SceneName, Group_Name=self.GroupName)

        source.addListener(Notificator.onInventoryUpdateItem)
