from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.ItemManager import ItemManager
from Notification import Notification


class SystemGetItemRoundFX(System):
    def __init__(self):
        super(SystemGetItemRoundFX, self).__init__()

        self.itemsRound = []

        self.Inventory = None
        pass

    def _onRun(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        self.addObserver(Notificator.onItemPopUp, self.__onItemPopUp)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        self.addObserver(Notificator.onZoomEnter, self.__onZoomEnter)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)

        return True
        pass

    def _onStop(self):
        self.__checkTasks()
        self.itemsRound = []
        pass

    def __onZoomEnter(self, zoomGroupName):
        self.__checkValidate()
        if len(self.itemsRound) == 0:
            return False
            pass

        return False
        pass

    def __onSceneEnter(self, sceneName):
        self.__checkValidate()

        return False
        pass

    def __onSceneLeave(self, sceneName):
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
        GetItemFade = DefaultManager.getDefaultFloat("GetItemFade", 0.3)
        time = 250.0

        with TaskManager.createTaskChain(Name="ItemPopUpRound", Cb=Functor(self.__removeRoundItem, itemName)) as tc:
            with GuardBlockGame(tc) as tc:
                tc.addTask("TaskSceneActivate")
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=True)

                with tc.addParallelTask(3) as (tc1, tc2, tc3):
                    tc1.addScope(self.scopeOpen, "ItemPopUp")
                    tc2.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=GetItemFade, Time=time, Block=True,
                                ReturnItem=False)
                    tc3.addTask("TaskItemPopUp", GroupName="ItemPopUp", ItemName=itemName)

                with tc.addParallelTask(3) as (tc1, tc2, tc3):
                    tc1.addScope(self.scopeClose, "ItemPopUp")

                    tc2.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=GetItemFade, Time=time, Unblock=True)
                    tc3.addScope(self.__addInventoryItem, itemName)

                tc.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=False)

    def __addInventoryItem(self, scope, itemName):
        scope.addTask("AliasInventoryAddInventoryItemFX", Inventory=self.Inventory, ItemName=itemName,
                      EffectPolicy="ActionGetItem")

    def __removeRoundItem(self, isSkip, itemName):
        self.__checkTasks()
        self.itemsRound.remove(itemName)
        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        Notification.notify(Notificator.onGetItem, self.Inventory, InventoryItem)
        self.__checkValidate()

    def __checkTasks(self):
        if TaskManager.existTaskChain("ItemPopUpRound") is True:
            TaskManager.cancelTaskChain("ItemPopUpRound")

    def scopeOpen(self, source, GropName):
        MovieName = "Movie2_Open"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)
            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)
