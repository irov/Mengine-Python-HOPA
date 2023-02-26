from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroPet(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        self.MovieName = values[1]
        self.SocketName = "Socket_Pet"
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (self.ItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))
                pass

            #        if self.hasObject(self.SocketName) is False:
            #            self.initializeFailed("MacroGiveItem not found Object %s in group %s"%(self.SocketName, self.GroupName))
            #            pass
            pass
        pass

    def _onGenerate(self, source):
        GroupInv = GroupManager.getGroup('Inventory')
        DemonPet = GroupInv.getObject('Demon_Pet')
        SocketPet = DemonPet.getObject(self.SocketName)

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")
        Quest = self.addQuest(source, "UsePet", SceneName=self.SceneName, Inventory=Inventory, GroupName=self.GroupName, InventoryItem=InventoryItem, Object=SocketPet)

        with Quest as tc_quest:
            tc_quest.addTask("AliasPetItem", Socket=SocketPet, ItemName=self.ItemName, SceneName=self.SceneName, Group_Name=self.GroupName, MovieName=self.MovieName)
            pass
        pass

    pass