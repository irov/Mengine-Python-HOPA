from Foundation.Notificator import Notificator
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.CruiseAction import CruiseAction


class CruiseActionWait(MixinGroup, CruiseAction):
    def _onAction(self, source):
        source.addListener(Notificator.onQuestRun)
        source.addNotify(Notificator.onCruiseActionEnd, self)
