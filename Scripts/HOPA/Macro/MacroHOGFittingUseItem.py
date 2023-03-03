from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGFittingUseItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        self.ItemUseName = values[2]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingUseItem Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingUseItem Item %s not found in Params" % (self.ItemName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemUseName) is False:
                self.initializeFailed("HOGFittingUseItem Item %s not found in Params" % (self.ItemUseName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ItemObject = HOGFittingItemManager.getItemSceneObject(self.ItemName)

        ItemUseObject = HOGFittingItemManager.getItemStoreObject(self.ItemUseName)

        EnigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)
        EnigmaEntity = EnigmaObject.getEntity()
        Inventory = EnigmaEntity.getInventory()

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=ItemUseObject, Object=ItemObject)
        with Quest as tc_quest:
            tc_quest.addTask("TaskHOGFittingItemUse", ItemObject=ItemObject, ItemUseObject=ItemUseObject)
            pass

    pass
