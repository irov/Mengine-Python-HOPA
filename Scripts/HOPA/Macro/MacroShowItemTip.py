from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TipManager import TipManager


class MacroShowItemTip(MacroCommand):
    def _onValues(self, values, **params):
        self.SocketName = values[0]
        self.ItemName = values[1]

        self.TipName = values[2]
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))
                pass

            FinderType, Object = self.findObject(self.SocketName)
            objtype = Object.getType()

            if objtype == "ObjectItem":
                SocketItemName = self.SocketName

                if ItemManager.hasItemObjectName(SocketItemName) is False:
                    self.initializeFailed("SocketItem %s not found Object" % (SocketItemName))
                    pass
            else:
                if self.hasObject(self.SocketName, params) is False:
                    self.initializeFailed("Socket %s not found in group %s" % (self.SocketName, params["GroupName"]))
                    pass
                pass

            if TipManager.hasTip(self.TipName) is False:
                self.initializeFailed("Tip %s not found" % (self.TipName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        policyPickInventoryItemEffectStop = PolicyManager.getPolicy("PickInventoryItemStop", "TaskDummy")

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")

        FinderType, Object = self.findObject(self.SocketName)

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=InventoryItem, Object=Object)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, Object, self.TipName)
            tc_quest.addTask("TaskSocketPlaceInventoryItem", SocketName=self.SocketName, InventoryItem=InventoryItem,
                             ItemName=self.ItemName, Taken=False, Pick=True)
            tc_quest.addTask(policyPickInventoryItemEffectStop, InventoryItem=InventoryItem)
            tc_quest.addNotify(Notificator.onTipRemoveWithoutParagraphs, self.TipName)
            pass
        pass

    pass
