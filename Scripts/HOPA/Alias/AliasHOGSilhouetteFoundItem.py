from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager


class AliasHOGSilhouetteFoundItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGSilhouetteFoundItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        InventoryFoundItems = HOGInventory.getFoundItems()
        FoundItems = self.HOG.getFoundItems()
        if self.HOGItemName in FoundItems and self.HOGItemName in InventoryFoundItems:
            self.log("invalid run, item %s already found" % (self.HOGItemName,))
            return
            pass

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName
        Item = self.Group.getObject(ItemName)
        ItemType = Item.getType()

        PolicyFoundEffect = None

        if ItemType is "ObjectItem":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGSilhouetteItemFoundEffect", "AliasHOGSilhouetteItemFoundEffect")
        elif ItemType is "ObjectMovieItem":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGSilhouetteMovieItemFoundEffect", "PolicyHOGRollingMovieItemFoundEffect")
        elif ItemType is "ObjectMovie2Item":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGSilhouetteMovie2ItemFoundEffect", "PolicyHOGRollingMovie2ItemFoundEffect")

            PolicyCheckMarkNearItem = PolicyManager.getPolicy("HOGSilhouetteICheckMark", "PolicyCheckMarkNearItem")

        source.addTask("TaskNotify", ID=Notificator.onHOGFoundItem, Args=(self.HOGItemName,))

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        if hogItem.objectName is not None:
            # source.addTask(PolicyCheckMarkNearItem, HOG = self.HOG, HOGItemName = self.HOGItemName, EnigmaName = self.EnigmaName)

            source.addTask(PolicyFoundEffect, HOG=self.HOG, HOGItemName=self.HOGItemName, EnigmaName=self.EnigmaName)

        source.addTask("TaskHOGFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName)
        source.addTask("TaskHOGInventoryFoundItem", HOGInventory=HOGInventory, HOGItemName=self.HOGItemName)
