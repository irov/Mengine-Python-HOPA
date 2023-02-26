from Foundation.Notificator import Notificator
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGFittingFindItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingFindItem Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingFindItem Item %s not found in Params" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ItemObject = HOGFittingItemManager.getItemSceneObject(self.ItemName)
        InventoryItemObject = HOGFittingItemManager.getItemStoreObject(self.ItemName)
        ItemObjectName = ItemObject.getName()
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName, ItemName=ItemObjectName)
        with Quest as tc_quest:
            tc_quest.addTask("TaskItemClick", Item=ItemObject)
            tc_quest.addTask("TaskItemPick", Item=ItemObject)
            tc_quest.addTask("TaskNotify", ID=Notificator.onItemPicked, Args=(ItemObject,))
            tc_quest.addTask("TaskNotify", ID=Notificator.onSoundEffectOnObject, Args=(ItemObject, "PickItem"))

            tc_quest.addTask("AliasHOGInventoryFittingAddItem", Enigma=Enigma, ItemObject=ItemObject, InventoryItemObject=InventoryItemObject, ItemName=self.ItemName)
            pass
        pass

    pass