from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject

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

    def _onAction(self, source):
        demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        pos = demon.getObject("Movie2Button_Ok").getCurrentMovieSocketCenter()
        move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionGetItem')

        source.addTask("AliasCruiseControlAction", Position=pos, Object=demon.getObject("Movie2Button_Ok"))
        source.addDelay(move_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
