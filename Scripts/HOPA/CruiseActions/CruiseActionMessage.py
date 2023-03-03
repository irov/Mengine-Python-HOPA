from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager

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

    def _onAction(self):
        obj = GroupManager.getObject("Message", self.Movie2ButtonName)
        pos = obj.getCurrentMovieSocketCenter()

        if TaskManager.existTaskChain("CruiseActionGetItem") is True:
            TaskManager.cancelTaskChain("CruiseActionGetItem")

        with TaskManager.createTaskChain(Name="CruiseActionGetItem") as tc:
            tc.addDelay(self.click_delay)

            if pos is not None:
                tc.addTask("AliasCruiseControlAction", Position=pos, Object=obj)

            tc.addDelay(self.move_delay)

            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionGetItem") is True:
            TaskManager.cancelTaskChain("CruiseActionGetItem")
