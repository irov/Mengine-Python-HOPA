from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager


class SystemGetItemRound(System):
    def __init__(self):
        super(SystemGetItemRound, self).__init__()

        self.itemsRound = []
        pass

    def _onRun(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        self.addObserver(Notificator.onItemPopUp, self.__onItemPopUp)
        self.addObserver(Notificator.onSceneActivate, self.__onSceneActivate)
        self.addObserver(Notificator.onZoomEnter, self.__onZoomEnter)
        self.addObserver(Notificator.onSceneDeactivate, self.__onSceneDeactivate)

        return True

    def _onStop(self):
        self.__checkTasks()
        self.itemsRound = []
        pass

    def __onZoomEnter(self, zoomGroupName):
        self.__checkValidate()
        if len(self.itemsRound) == 0:
            return False

        return False

    def __onSceneActivate(self, sceneName):
        self.__checkValidate()

        return False

    def __onSceneDeactivate(self, sceneName):
        self.__checkTasks()

        return False

    def __onItemPopUp(self, itemName):
        self.itemsRound.append(itemName)
        self.__checkValidate()

        return False

    def __checkValidate(self):
        countItems = len(self.itemsRound)

        if countItems == 0:
            return

        if TaskManager.existTaskChain("ItemPopUpRound") is True:
            return

        if SceneManager.isCurrentSceneActive() is False:
            return

        hasItemPopUpScene = SceneManager.hasLayerScene("ItemPopUp")

        if hasItemPopUpScene is False:
            return

        nextItemName = self.itemsRound[0]

        self.__startPopUp(nextItemName)

    def __startPopUp(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        with TaskManager.createTaskChain(Name="ItemPopUpRound", Cb=self.__removeRoundItem) as tc:
            with GuardBlockGame(tc) as source:
                source.addTask("TaskSceneActivate")

                source.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.3, Time=0.2 * 1000.0,
                               Block=True)  # speed fix

                source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=True)

                with source.addFork() as source_fork:
                    source_fork.addTask("TaskItemPopUp", GroupName="ItemPopUp", ItemName=itemName)
                    source_fork.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=False)
                    source_fork.addTask("AliasFadeOut", FadeGroupName="FadeDialog", To=0.3, Time=0.2 * 1000.0)

                source.addListener(Notificator.onItemPopUpEnd)

                with GuardBlockInput(source) as guard_source:
                    guard_source.addScope(self.__addInventoryItem, itemName)
                    guard_source.addNotify(Notificator.onInventoryAddItem, self.Inventory, InventoryItem)
                    guard_source.addNotify(Notificator.onGetItem, self.Inventory, InventoryItem)

    def __addInventoryItem(self, scope, itemName):
        self.itemsRound.remove(itemName)
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")
        self.Inventory.setParam("BlockScrolling", True)

        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        if self.Inventory.hasInventoryItem(InventoryItem) is False:
            InventoryItemIndex = len(InventoryItems)
        else:
            InventoryItemIndex = self.Inventory.indexInventoryItem(InventoryItem)

        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NewSlotIndex:
            scope.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
            scope.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NewSlotIndex)
            scope.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)

        with scope.addParallelTask(2) as (scope_fade_out, scope_get_item):
            scope_fade_out.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.3, Time=0.2 * 1000,
                                   Unblock=True)  # speed fix

            scope_get_item.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=itemName)
            scope_get_item.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory,
                                   InventoryItem=InventoryItem)
            scope_get_item.addTask("TaskEnable", Object=InventoryItem, Value=False)

            scope_get_item.addTask("TaskEffectInventoryAddInventoryItem", Inventory=self.Inventory,
                                   InventoryItem=InventoryItem)
            scope_get_item.addTask("TaskEnable", Object=InventoryItem, Value=True)

        scope.addFunction(self.Inventory.setParam, "BlockScrolling", False)

        if Mengine.hasResource("ItemToSlot") is True:
            scope.addTask("TaskSoundEffect", SoundName="ItemToSlot", Wait=False)

    def __removeRoundItem(self, isSkip):
        self.__checkTasks()
        self.__checkValidate()

    def __checkTasks(self):
        if TaskManager.existTaskChain("ItemPopUpRound") is True:
            TaskManager.cancelTaskChain("ItemPopUpRound")
