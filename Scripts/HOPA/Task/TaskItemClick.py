from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from Notification import Notification

class TaskItemClick(MixinItem, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskItemClick, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        self.TradeMode = params.get("Trade", False)
        self.Filter = params.get("Filter", None)
        pass

    def _onInitialize(self):
        super(TaskItemClick, self)._onInitialize()
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Item.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onItemClick, self._onItemFindFilter, self.Item)

        return False

    def _onFinally(self):
        super(TaskItemClick, self)._onFinally()

        if self.AutoEnable is True:
            self.Item.setInteractive(False)
            pass
        pass

    def _onItemFindFilter(self, item, *args):
        if self.Filter is not None:
            if self.Filter(item) is False:
                return False

        if ArrowManager.emptyArrowAttach() is False:
            if self.TradeMode:
                Notification.notify(Notificator.onAttachTrade)
                return True

            return False

        return True
