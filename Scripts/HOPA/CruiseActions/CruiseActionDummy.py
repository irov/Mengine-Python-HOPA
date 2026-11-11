from Foundation.Notificator import Notificator
from HOPA.CruiseAction import CruiseAction


class CruiseActionDummy(CruiseAction):
    def _onAction(self, source):
        source.addListener(Notificator.onQuestEnd, Filter=lambda quest: quest == self.Quest)
        source.addNotify(Notificator.onCruiseActionEnd, self)
