from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager


class AliasHOGRollingFoundItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGRollingFoundItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.EnigmaName = params.get("EnigmaName")

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        InventoryFoundItems = HOGInventory.getFoundItems()
        FoundItems = self.HOG.getFoundItems()
        if self.HOGItemName in FoundItems and self.HOGItemName in InventoryFoundItems:
            self.log("invalid run, item %s already found" % (self.HOGItemName,))
            return

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName
        Item = self.Group.getObject(ItemName)

        ItemType = Item.getType()

        PolicyFoundEffect = None
        PolicyCheckMarkNearItem = None
        if ItemType is "ObjectItem":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGRollingItemFoundEffect", "AliasHOGRollingItemFoundEffect")
            PolicyCheckMarkNearItem = PolicyManager.getPolicy("HOGRollingCheckMark", "PolicyCheckMarkNearItem")
        elif ItemType is "ObjectMovieItem":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGRollingMovieItemFoundEffect", "PolicyHOGRollingMovieItemFoundEffect")
            PolicyCheckMarkNearItem = PolicyManager.getPolicy("HOGRollingMovieItemCheckMark", "PolicyCheckMarkNearMovieItem")
        elif ItemType is "ObjectMovie2Item":
            PolicyFoundEffect = PolicyManager.getPolicy("HOGRollingMovie2ItemFoundEffect", "PolicyHOGRollingMovie2ItemFoundEffect")

        PolicyDeleteItemFromInventory = PolicyManager.getPolicy("HOGRollingDeleteItemFromInventory",
                                                                "PolicyDeleteItemFromInventory")

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        if hogItem.objectName is not None:
            source.addTask("TaskHOGFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName)
            source.addTask(PolicyFoundEffect, HOG=self.HOG, HOGItemName=self.HOGItemName, EnigmaName=self.EnigmaName)
            source.addNotify(Notificator.onHOGFoundItem, self.HOGItemName)
            source.addTask(PolicyDeleteItemFromInventory, HOG=self.HOG, HOGItemName=self.HOGItemName, EnigmaName=self.EnigmaName)
            source.addTask("TaskHOGInventoryFoundItem", HOGInventory=HOGInventory, HOGItemName=self.HOGItemName)
