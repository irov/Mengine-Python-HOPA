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

        self.Element = params.get("Element")
        self.TipName = params.get("TipName")

    def _onRun(self):
        if Mengine.hasTouchpad():
            self.addObserverFilter(Notificator.onSocketClickUp, self._onSocketClickFilter, self.Socket)
        else:
            self.addObserverFilter(Notificator.onSocketClick, self._onSocketClickFilter, self.Socket)

        return False

    def _onFinally(self):
        super(TaskSocketPickElementalMagic, self)._onFinally()

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
            Trace.msg_dev("<DEV> Can't get element {}, because user already has element {}".format(self.Element, player_element))
            TipManager.showTip(self.TipName)
            return False

        # check if user has quest on this magic
        quests = ElementalMagicManager.getMagicUseQuests()
        for quest in quests:
            if quest.params["Element"] == self.Element:
                Notification.notify(Notificator.onElementalMagicPick, self.Element)
                Trace.msg_dev("<DEV> Allow to get element {}, because user has Use quest at ({}, {}) [{}]".format(self.Element, quest.params["SceneName"], quest.params["GroupName"], quest.params["MagicId"]))
                return True

        TipManager.showTip(self.TipName)
        Trace.msg_dev("<DEV> Can't get element {}, because user hasn't Use quest for element {} (total quests {})\n{}".format(self.Element, player_element, len(quests), quests))

        return False
