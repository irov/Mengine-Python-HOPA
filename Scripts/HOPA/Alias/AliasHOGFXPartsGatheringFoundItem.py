from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager

class AliasHOGFXPartsGatheringFoundItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGFXPartsGatheringFoundItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.EnigmaName = params.get("EnigmaName")

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        InventoryFoundItems = HOGInventory.getFoundItems()
        if self.HOGItemName in InventoryFoundItems:
            self.log("invalid run, item %s already found" % (self.HOGItemName,))
            return

        PolicyFoundEffect = PolicyManager.getPolicy("HOGFXPartsGatheringItemFoundEffect", "AliasHOGFXPartsGatheringItemFoundEffect")

        source.addTask("TaskNotify", ID=Notificator.onHOGFoundItem, Args=(self.HOGItemName,))
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        if hogItem.objectName is not None:
            source.addTask(PolicyFoundEffect, HOG=self.HOG, HOGItemName=self.HOGItemName, EnigmaName=self.EnigmaName)