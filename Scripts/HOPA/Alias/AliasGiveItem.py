from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager
from HOPA.ItemUseManager import ItemUseManager


class AliasGiveItem(TaskAlias):
    def _onParams(self, params):
        super(AliasGiveItem, self)._onParams(params)
        #    Param Block
        self.Object = params.get("Object")
        self.SocketName = params.get("SocketName")
        self.ItemName = params.get("ItemName")

    def _onGenerate(self, source):
        ObjectName = self.Object.getName()
        ObjectType = self.Object.getType()

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        PopItemName = None
        Movie_Open = None

        if ItemUseManager.hasItem(self.ItemName) is True:
            PopItemName = ItemUseManager.getPopItem(self.ItemName, self.SocketName)
            Movie_Open = ItemUseManager.getMovie(self.ItemName, self.SocketName)

        if ObjectType == "ObjectSocket":
            source.addTask("TaskSocketPlaceInventoryItem", SocketName=ObjectName, InventoryItem=InventoryItem,
                           ItemName=self.ItemName, Taken=True, Pick=False)

            if Movie_Open is not None:
                source.addTask("TaskMoviePlay", Movie=Movie_Open, Wait=True)
                source.addTask("TaskMoviePlay", Movie=Movie_Open, Reverse=True, Wait=True)

            if PopItemName is not None:
                source.addTask("AliasInventoryGetInventoryItem", ItemName=PopItemName)

        elif ObjectType == "ObjectItem":
            source.addTask("TaskItemPlaceInventoryItem", ItemName=ObjectName,
                           InventoryItem=InventoryItem, Taken=True, Pick=False)

        elif ObjectType == "ObjectTransition":
            source.addTask("TaskTransitionGiveInventoryItem", TransitionName=ObjectName, InventoryItem=InventoryItem)

        elif ObjectType == "ObjectZoom":
            source.addTask("TaskZoomGiveInventoryItem", ZoomName=ObjectName, InventoryItem=InventoryItem)
