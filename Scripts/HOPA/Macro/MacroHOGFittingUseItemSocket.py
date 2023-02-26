from Foundation.GroupManager import GroupManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGFittingUseItemSocket(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.SocketName = values[1]
        self.ItemUseName = values[2]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingUseItemSocket Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("HOGFittingUseItemSocket not found Socket %s in group %s in Params" % (self.SocketName, self.GroupName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemUseName) is False:
                self.initializeFailed("HOGFittingUseItemSocket Item %s not found in Params" % (self.ItemUseName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        def __startQuest(scope):
            ItemUseObject = HOGFittingItemManager.getItemStoreObject(self.ItemUseName)
            EnigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)
            EnigmaEntity = EnigmaObject.getEntity()
            Inventory = EnigmaEntity.getInventory()
            # Inventory = DemonManager.getDemon("HOGInventoryFitting")
            Socket = GroupManager.getObject(self.GroupName, self.SocketName)

            Quest = self.addQuest(scope, "UseHOGFittingItem", SceneName=self.SceneName, Inventory=Inventory, GroupName=self.GroupName, InventoryItem=ItemUseObject, Object=Socket)
            with Quest as tc_quest:
                tc_quest.addTask("TaskHOGFittingItemUseSocket", SocketName=self.SocketName, ItemUseObject=ItemUseObject)
                pass
            pass

        source.addTask("TaskScope", Scope=__startQuest)

        pass

    pass