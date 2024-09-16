from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskItemPlaceItem(MixinItem, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskItemPlaceItem, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)

        self.SocketItem = params.get("SocketItem")
        self.taken = params.get("Taken", True)
        self.pick = params.get("Pick", False)
        self.accuracy = params.get("Accuracy", 0)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.SocketItem.setInteractive(True)
            pass

        # remove onSocketClickEndUp for Touchpad because it causes bugs in click+click
        self.addObserverFilter(Notificator.onItemClick, self._onItemClickFilter, self.SocketItem)

        return False
        pass

    def _onItemClickFilter(self, item):
        attach = ArrowManager.getArrowAttach()

        if attach is None or attach is not self.Item:
            return False

        if self.accuracy == 0:
            return True
            pass

        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        ItemEntity = self.SocketItem.getEntity()
        Image = ItemEntity.getSprite()
        centre = Image.getLocalImageCenter()
        itemPos = self.Item.getPosition()
        SocketPos = self.SocketItem.getPosition()
        arowPos = arrow_node.getWorldPosition()
        condition = (
            itemPos[0] + arowPos[0] - SocketPos[0] - centre[0],
            itemPos[0] + arowPos[0] - SocketPos[0] - centre[0]
        )
        if (condition[0] ** 2 + condition[1] ** 2) ** 0.5 < self.accuracy:
            return True
            pass
        return False
        pass

    def _onFinally(self):
        super(TaskItemPlaceItem, self)._onFinally()

        if self.AutoEnable is True:
            self.SocketItem.setInteractive(False)