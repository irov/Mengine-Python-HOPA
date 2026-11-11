from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject

from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionMessage(CruiseAction, MixinObject):

    def _onParams(self, params):
        super(CruiseActionMessage, self)._onParams(params)

        self.SelectYesChoice = bool(params.get("SelectYesChoice", False))
        self.Movie2ButtonName = "Movie2Button_Yes" if self.SelectYesChoice else "Movie2Button_No"

        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionMessage')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionMessage')

    def _onCheck(self):
        return GroupManager.getObject("Message", self.Movie2ButtonName).isActive()

    def _onAction(self, source):
        obj = GroupManager.getObject("Message", self.Movie2ButtonName)
        pos = obj.getCurrentMovieSocketCenter()

        source.addDelay(self.click_delay)

        if pos is not None:
            source.addTask("AliasCruiseControlAction", Position=pos, Object=obj)

        source.addDelay(self.move_delay)

        source.addNotify(Notificator.onCruiseActionEnd, self)
