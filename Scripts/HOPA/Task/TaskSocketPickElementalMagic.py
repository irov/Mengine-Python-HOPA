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

        self.AutoEnable = params.get("AutoEnable", True)
        self.Element = params.get("Element")
        self.TipName = params.get("TipName")

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)

        if Mengine.hasTouchpad():
            self.addObserverFilter(Notificator.onSocketClickUp, self._onSocketClickFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

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
            TipManager.showTip(self.TipName)
            return False

        # check if user has quest on this magic
        quests = ElementalMagicManager.getMagicUseQuests()
        for quest in quests:
            if quest.params["Element"] == player_element:
                Trace.msg_dev("<DEV> Allow to get element, because user has Use quest at ({}, {}) [{}]".format(quest.params["SceneName"], quest.params["GroupName"], quest.params["MagicId"]))
                return True

        TipManager.showTip(self.TipName)
        Trace.msg_dev("<DEV> Can't get this element, because user hasn't Use quest for element [{}] (total quests {})".format(player_element, len(quests)))

        return False
