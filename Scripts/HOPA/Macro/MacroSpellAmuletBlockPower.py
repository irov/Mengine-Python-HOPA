from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager


class MacroSpellAmuletBlockPower(MacroCommand):
    def _onValues(self, values):
        self.power_name = values[0]

        self.notificator = Notificator.onSpellAmuletBlockPower

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellsManager.getSpellAmuletPowerParam(self.power_name) is None:
                self.initializeFailed("MacroSpellAmuletBlockPower SpellsManager: not found power '{}'".format(self.power_name))
                pass
            pass

    def __macroCompleteFilter(self, caller, *args):
        if caller != self.notificator:
            return False

        if args[0] != self.power_name:
            return False

        return True

    def _onGenerate(self, source):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(Notificator.onSpellMacroComplete, Filter=self.__macroCompleteFilter)
            parallel_1.addNotify(self.notificator, self.power_name)
