from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager

from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionGetItem(CruiseAction, MixinObject):

    def _onCheck(self):
        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")

        if not Demon.isActive():
            return False

        Object = Demon.getObject("Movie2Button_Ok")

        if not Object.isActive():
            return False

        return True

    def _onAction(self):
        demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        pos = demon.getObject("Movie2Button_Ok").getCurrentMovieSocketCenter()
        move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionGetItem')

        if TaskManager.existTaskChain("CruiseActionGetItem") is True:
            TaskManager.cancelTaskChain("CruiseActionGetItem")

        with TaskManager.createTaskChain(Name="CruiseActionGetItem") as tc:
            tc.addTask("AliasCruiseControlAction", Position=pos, Object=demon.getObject("Movie2Button_Ok"))
            tc.addDelay(move_delay)
            tc.addNotify(Notificator.onCruiseActionEnd, self)

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionGetItem") is True:
            TaskManager.cancelTaskChain("CruiseActionGetItem")
