from Foundation.Notificator import Notificator
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class AliasFindItem(TaskAlias):
    def __init__(self):
        super(AliasFindItem, self).__init__()

    def _onParams(self, params):
        super(AliasFindItem, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.SceneName = params.get("SceneName")
        self.Inventory = params.get("Inventory")

    def _onInitialize(self):
        super(AliasFindItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ItemManager.hasItemObject(self.ItemName) is False:
                self.initializeFailed("ItemName '%s' not found" % self.ItemName)
                pass
            pass

    def _onGenerate(self, source):
        ItemObject = ItemManager.getItemObject(self.ItemName)
        ObjectType = ItemObject.getType()

        if ObjectType is "ObjectMovieItem" or ObjectType is "ObjectMovie2Item":
            source.addParam(ItemObject, "Interactive", 1)
            source.addTask("TaskMovieItemClickOBS", MovieItem=ItemObject)
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addScope(self.scopeInventory_Scrolling)
                parallel_2.addTask("TaskMovieItemPick", MovieItem=ItemObject)
        else:
            PolicyClickItem = PolicyManager.getPolicy("ClickItem", "TaskItemClick")
            source.addTask(PolicyClickItem, Item=ItemObject)
            source.addTask("TaskItemPick", Item=ItemObject)

        source.addTask("TaskNotify", ID=Notificator.onInventoryRise)
        source.addTask("TaskNotify", ID=Notificator.onItemPicked, Args=(ItemObject,))
        source.addNotify(Notificator.onSoundEffectOnObject, ItemObject, "PickItem")

    def scopeInventory_Scrolling(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")
        BlockScrolling = self.Inventory.getParam("BlockScrolling")

        if self.Inventory.hasInventoryItem(InventoryItem) is False:
            InventoryItemIndex = len(InventoryItems)
        else:
            InventoryItemIndex = self.Inventory.indexInventoryItem(InventoryItem)

        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount
        if CurrentSlotIndex != NewSlotIndex:
            PolicyInventoryChangeCurrentSlotIndex = PolicyManager.getPolicy("InventoryChangeCurrentSlotIndex", "AliasInventoryChangeCurrentSlotIndex")
            if BlockScrolling:
                source.addListener(Notificator.onInventoryUpdateItem)
            source.addTask(PolicyInventoryChangeCurrentSlotIndex, Inventory=self.Inventory,
                           ItemName=self.ItemName, NewSlotIndex=NewSlotIndex)
