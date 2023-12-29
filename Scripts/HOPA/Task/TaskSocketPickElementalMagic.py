from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.TipManager import TipManager


class TaskSocketPickElementalMagic(MixinSocket, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskSocketPickElementalMagic, self)._onParams(params)

        self.Element = params["Element"]
        self.MagicId = params["MagicId"]
        self.TipName = params.get("TipName")
        self.AutoEnable = params.get("AutoEnable", True)

    def _onRun(self):
        if Mengine.hasTouchpad():
            self.addObserverFilter(Notificator.onSocketClickUp, self._onSocketClickFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

        if self.AutoEnable is True:
            self.Socket.setInteractive(True)
        return False

    def _onFinally(self):
        super(TaskSocketPickElementalMagic, self)._onFinally()
        if self.AutoEnable is True:
            self.Socket.setInteractive(False)

    def _onSocketClickFilter(self, socket):
        attach = ArrowManager.getArrowAttach()

        if attach is None or attach.getName() != "ElementalMagicRing":
            TipManager.showTip(ElementalMagicManager.getConfig("TipPickMagicNeedRing", "ID_Tip_Magic_NeedRing"))
            return False

        ring = ElementalMagicManager.getMagicRing()

        if ring is None:  # check active
            return False

        player_element = ElementalMagicManager.getPlayerElement()

        if player_element is not None:
            Trace.msg_dev("<DEV> Can't get element {!r} [{}], because user already has element {!r}".format(
                self.Element, self.MagicId, player_element))
            TipManager.showTip(self.TipName)
            return False

        if self.hasActiveUseQuest() is False:
            Trace.msg_dev("<DEV> Can't get element {!r} [{}], because user hasn't Use quest for element {!r}".format(
                self.Element, self.MagicId, player_element))
            TipManager.showTip(self.TipName)
            return False

        Notification.notify(Notificator.onElementalMagicPick, self.Element, self.MagicId)
        Trace.msg_dev("<DEV> Allow to get element {!r} [{}], because user has Use quest for this element".format(
            self.Element, self.MagicId))

        return True

    def hasActiveUseQuest(self):
        if ElementalMagicManager.isMagicUsed(self.MagicId) is True:
            Trace.msg_dev("<DEV> Element {!r} [{}] was used earlier - allow pick action to prevent game stuck".format(
                self.Element, self.MagicId))
            return True
        return ElementalMagicManager.hasUseQuestOnElement(self.MagicId) is True
