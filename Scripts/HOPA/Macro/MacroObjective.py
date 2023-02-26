from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.ObjectiveManager import ObjectiveManager

class MacroObjective(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 1:
                self.initializeFailed("Macro%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ObjectiveID = values[0]
        self.Notifies = [value for value in values[1:] if value is not None]

    def _onInitialize(self):
        if ObjectiveManager.hasObjective(self.ObjectiveID) is False:
            self.initializeFailed("Objective %s not found" % (self.ObjectiveID))
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasObjectives", ObjectiveID=self.ObjectiveID, Notifies=self.Notifies)
        pass

    pass