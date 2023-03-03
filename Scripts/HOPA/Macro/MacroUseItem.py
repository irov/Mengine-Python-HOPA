from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroUseItem(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroUseItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.SocketName)
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")

        ObjectName = Object.getName()
        ObjectType = Object.getType()

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=InventoryItem, Object=Object)

        with Quest as tc_quest:
            if ObjectType == "ObjectSocket":
                tc_quest.addTask("TaskSocketPlaceInventoryItem", SocketName=ObjectName, InventoryItem=InventoryItem,
                                 ItemName=self.ItemName, Taken=False, Pick=False)
                pass
            elif ObjectType == "ObjectItem":
                tc_quest.addTask("TaskItemPlaceInventoryItem", ItemName=ObjectName, InventoryItem=InventoryItem,
                                 Taken=False, Pick=False)
                pass
            pass

        source.addListener(Notificator.onInventoryUpdateItem)

        pass

    pass
