from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskHOGFittingItemUseSocket(MixinSocket, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskHOGFittingItemUseSocket, self)._onParams(params)
        self.ItemUseObject = params.get("ItemUseObject")
        self.Inventory = DemonManager.getDemon("HOGInventoryFitting")
        pass

    def _onRun(self):
        self.Socket.setInteractive(True)

        if Mengine.hasTouchpad():
            # touchpad hot fix
            self.addObserverFilter(Notificator.onSocketClickEndUp, self._onSocketFindFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketFindFilter, self.Socket)

        return False
        pass

    def _onSocketFindFilter(self, socket):
        if ArrowManager.emptyArrowAttach() is True:
            return False
            pass

        attach = ArrowManager.getArrowAttach()

        if attach is not self.ItemUseObject:
            return False
            pass

        inv_Ent = self.Inventory.getEntity()
        inv_Ent.ItemIsValideUse = True
        return True
        pass

    def _onFinally(self):
        super(TaskHOGFittingItemUseSocket, self)._onFinally()

        self.Socket.setInteractive(False)
        pass

    pass
