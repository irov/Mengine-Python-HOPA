from HOPA.HintManager import HintManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHintMind(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 2:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ExceptionId = values[0]

        self.Notifies = [value for value in values[1:] if value is not None]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if HintManager.hasSceneException(self.ExceptionId) is False:
                self.initializeFailed("HintManager %s not found" % self.ExceptionId)
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onHintSceneException, self.ExceptionId, self.SceneName, self.GroupName, self.Notifies)
        pass

    pass
