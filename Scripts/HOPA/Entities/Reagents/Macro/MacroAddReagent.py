from Foundation.DemonManager import DemonManager
from HOPA.Entities.Reagents.ReagentsManager import ReagentsManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroAddReagent(MacroCommand):
    def _onValues(self, values):
        self.reagentName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ReagentsManager.hasReagent(self.reagentName) is False:
                self.initializeFailed("Reagent %s not found" % (self.reagentName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Demon = DemonManager.getDemon("Reagents")

        source.addTask("TaskAppendParam", Object=Demon, Param="OpenReagents", Value=self.reagentName)
        pass
    pass