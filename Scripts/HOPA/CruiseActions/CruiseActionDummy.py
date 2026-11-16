from Foundation.Notificator import Notificator
from HOPA.CruiseAction import CruiseAction


class CruiseActionDummy(CruiseAction):
    def _onParams(self, params):
        super(CruiseActionDummy, self)._onParams(params)
        self.duration = params.get("Duration", 0.0)
        pass

    def getTimeout(self):
        return super(CruiseActionDummy, self).getTimeout() + self.duration

    def _onAction(self, source):
        source.addListener(Notificator.onQuestEnd, Filter=lambda quest: quest == self.Quest)
        source.addNotify(Notificator.onCruiseActionEnd, self)
