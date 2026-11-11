from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TipManager import TipManager


class MacroUseItemTip(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemName = values[1]

        self.TipName = values[2]
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

            if TipManager.hasTip(self.TipName) is False:
                self.initializeFailed("Tip %s not found" % (self.TipName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        def __removeTipGuard(value, TipName):
            if value is True:
                return

            Notification.notify(Notificator.onTipRemoveWithoutParagraphs, TipName)

        FinderType, Object = self.findObject(self.SocketName)

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")

        ObjectName = Object.getName()
        ObjectType = Object.getType()

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=InventoryItem, Object=Object)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, Object, self.TipName)

            # the guard removes the tip on every exit, also when the scenario chain is cancelled
            tc_guard = tc_quest.makeGuardSource(True, __removeTipGuard, self.TipName)
            if ObjectType == "ObjectSocket":
                tc_guard.addTask("TaskSocketPlaceInventoryItem", SocketName=ObjectName, InventoryItem=InventoryItem,
                                 ItemName=self.ItemName, Taken=False, Pick=False)
                pass
            elif ObjectType == "ObjectItem":
                tc_guard.addTask("TaskItemPlaceInventoryItem", ItemName=ObjectName, InventoryItem=InventoryItem,
                                 Taken=False, Pick=False)
                pass
            pass

        source.addListener(Notificator.onInventoryUpdateItem)
        pass

    pass
