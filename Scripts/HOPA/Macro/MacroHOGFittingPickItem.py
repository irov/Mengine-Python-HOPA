from Foundation.Notificator import Notificator
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGFittingPickItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingPickItem Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingPickItem Item %s not found in Params" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ItemObject = HOGFittingItemManager.getItemSceneObject(self.ItemName)
        InventoryItemObject = HOGFittingItemManager.getItemStoreObject(self.ItemName)
        ItemObjectName = ItemObject.getName()

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName,
                              ItemName=ItemObjectName)
        with Quest as tc_quest:
            tc_quest.addTask("TaskItemPick", Item=ItemObject)
            tc_quest.addNotify(Notificator.onItemPicked, ItemObject)
            tc_quest.addNotify(Notificator.onSoundEffectOnObject, ItemObject, "PickItem")

            Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)
            tc_quest.addTask("AliasHOGInventoryFittingAddItem", Enigma=Enigma, ItemObject=ItemObject,
                             InventoryItemObject=InventoryItemObject, ItemName=self.ItemName)
            pass
        pass

    pass
