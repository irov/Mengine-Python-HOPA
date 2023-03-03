from Foundation.ArrowManager import ArrowManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.QuestManager import QuestManager


class TaskSocketPlaceInventoryAccumulateItem(MixinSocket, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskSocketPlaceInventoryAccumulateItem, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        self.InventoryItem = params.get("InventoryItem")
        self.ItemName = params.get("ItemName", None)
        self.Value = params.get("Value")
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

        return False
        pass

    def _onFinally(self):
        super(TaskSocketPlaceInventoryAccumulateItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Socket.setInteractive(False)
            pass
        pass

    def _onSocketClickFilter(self, socket):
        sceneName = SceneManager.getCurrentSceneName()
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False
            pass

        if self.InventoryItem is not attach:
            hasQuest = QuestManager.hasActiveGiveItem(sceneName, self.GroupName, "UseInventoryItem", attach, self.Socket)

            if hasQuest is False:
                attachEntity = attach.getEntity()
                attachEntity.invalidUse(socket)
                pass

            return False
            pass

        arrowItemEntity = self.InventoryItem.getEntity()

        if self.ItemName is not None:
            if self.InventoryItem.reduceValue(self.Value) == "back":
                arrowItemEntity.pickAfterPlace()
                pass
            elif self.InventoryItem.reduceValue(self.Value) == "take":
                arrowItemEntity.take()
                pass
            else:
                arrowItemEntity.invalidUse()
                return False
                pass
            pass

        return True
        pass

    pass
