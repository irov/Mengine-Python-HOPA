from Foundation.ArrowManager import ArrowManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.QuestManager import QuestManager


ALLOWED_OBJECT_TYPES = ["ObjectInventoryItem", "ObjectInventoryItemAccumulate", "ObjectInventoryCountItem"]


class TaskSocketPlaceInventoryItem(MixinSocket, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskSocketPlaceInventoryItem, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        self.InventoryItem = params.get("InventoryItem")
        self.ItemName = params.get("ItemName", None)
        self.Taken = params.get("Taken", True)
        self.Pick = params.get("Pick", False)

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)

        if Mengine.hasTouchpad():
            # touchpad hot fix
            self.addObserverFilter(Notificator.onSocketClickUp, self._onSocketClickFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

        return False

    def _onFinally(self):
        super(TaskSocketPlaceInventoryItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Socket.setInteractive(False)

    def _onSocketClickFilter(self, socket):
        sceneName = SceneManager.getCurrentSceneName()
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False

        attachType = attach.getType()
        if attachType not in ALLOWED_OBJECT_TYPES:
            return False

        if self.InventoryItem is not attach:
            # ScenePlus fix
            if SystemManager.hasSystem("SystemItemPlusScene") is True:
                SystemItemPlusScene = SystemManager.getSystem("SystemItemPlusScene")
                SocketGroupName = self.Socket.getGroup()
                if SystemItemPlusScene.Open_Zoom is not None:
                    ScenePlusGroupName, ScenePlusName, _ = SystemItemPlusScene.Open_Zoom
                    if ScenePlusGroupName == SocketGroupName:
                        sceneName = ScenePlusName
            #

            hasQuest = QuestManager.hasActiveGiveItem(sceneName, self.GroupName, "UseInventoryItem", attach, self.Socket)

            if hasQuest is False:
                questList = QuestManager.getObjectActiveGiveItemQuestList(sceneName, self.GroupName, "UseInventoryItem", self.Socket)

                # ensure that only one fail will be executed when there exists multiple parallel quests on socket
                for quest in questList:
                    item = quest.params.get("InventoryItem")

                    if item is not None:  # safety measure: brake on first Valid item instead of questList[0]
                        if attach != self.InventoryItem and self.InventoryItem == item:
                            attachEntity = attach.getEntity()

                            if attachEntity is not None:
                                attachEntity.invalidUse(socket)  # call invalid inventory item use

                        break

            return False

        if self.ItemName is not None:
            if self.InventoryItem.hasItem(self.ItemName) is False:
                return False

        arrowItemEntity = self.InventoryItem.getEntity()

        if arrowItemEntity is None:  # check active
            return False

        # - fix for count item --------------------------
        # - takes item only when it is full
        # -----------------------------------------------
        if arrowItemEntity.checkCount() is False:
            return False
        # -----------------------------------------------

        if self._actionEnergy() is False:
            return False

        if self.ItemName is not None:
            if self.InventoryItem.takeItem(self.ItemName) is True:
                if self.Taken is True:
                    arrowItemEntity.take()
                else:
                    if self.Pick is False:
                        arrowItemEntity.place()
            else:
                arrowItemEntity.take()

        return True

    def _actionEnergy(self):
        if SystemManager.hasSystem("SystemEnergy") is False:
            return True
        SystemEnergy = SystemManager.getSystem("SystemEnergy")

        if SystemEnergy.performAction("PlaceItem") is True:
            # if 'PlaceItem' not enabled or this mechanic is disabled it also return True
            return True
        return False
