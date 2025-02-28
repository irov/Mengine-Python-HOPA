from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroRemoveReagentPaper(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        Demon = DemonManager.getDemon("ReagentsButton")
        source.addParam(Demon, "EnablePaper", False)
        pass

    pass
