from Foundation.Notificator import Notificator
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionShiftCollect(CruiseAction):
    def _onCheck(self):
        return True

    def _onAction(self, source):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionShiftCollect')

        source.addDelay(click_delay)
        source.addNotify(Notificator.onShiftCollectSkip)
        source.addNotify(Notificator.onCruiseActionEnd, self)
