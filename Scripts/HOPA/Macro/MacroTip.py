from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TipManager import TipManager


class MacroTip(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 2:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ObjectName = values[0]
        self.TipName = values[1]

        self.Notifies = [value for value in values[2:] if value is not None]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if TipManager.hasTip(self.TipName) is False:
                self.initializeFailed("Tip %s not found" % (self.TipName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasTipPlay", TipID=self.TipName, ObjectName=self.ObjectName, Notifies=self.Notifies)
        pass

    pass
