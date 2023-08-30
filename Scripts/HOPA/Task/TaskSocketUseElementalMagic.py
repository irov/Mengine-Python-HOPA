from Foundation.ArrowManager import ArrowManager
from Foundation.Notificator import Notificator
from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.Entities.ElementalMagic.Ring import InvalidClick


class TaskSocketUseElementalMagic(MixinSocket, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskSocketUseElementalMagic, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        self.Element = params.get("Element")

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)

        if Mengine.hasTouchpad():
            self.addObserverFilter(Notificator.onSocketClickUp, self._onSocketClickFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

        return False

    def _onFinally(self):
        super(TaskSocketUseElementalMagic, self)._onFinally()

        if self.AutoEnable is True:
            self.Socket.setInteractive(False)

    def _onSocketClickFilter(self, socket):
        attach = ArrowManager.getArrowAttach()

        if attach is None:
            return False

        if attach.getName() != "ElementalMagicRing":
            return False

        ring = ElementalMagicManager.getMagicRing()

        if ring is None:  # check active
            return False

        player_element = ElementalMagicManager.getPlayerElement()

        if player_element is None:
            Notification.notify(Notificator.onElementalMagicInvalidClick, InvalidClick.EmptyRing)
            return False

        if self.Element != player_element:
            Notification.notify(Notificator.onElementalMagicInvalidClick, InvalidClick.WrongElement)
            return False

        if self._actionEnergy() is False:
            return False

        Notification.notify(Notificator.onElementalMagicUse, player_element)

        return True

    def _actionEnergy(self):
        if SystemManager.hasSystem("SystemEnergy") is False:
            return True
        SystemEnergy = SystemManager.getSystem("SystemEnergy")

        if SystemEnergy.performAction("ElementalMagic") is True:
            return True
        return False
