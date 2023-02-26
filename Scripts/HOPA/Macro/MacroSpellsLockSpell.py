from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager

class MacroSpellsLockSpell(MacroCommand):
    def _onValues(self, values):
        self.spell_type = values[0]

        self.notificator = Notificator.onSpellUISpellLock

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellsManager.getSpellsUIButtonParam(self.spell_type) is None:
                self.initializeFailed("MacroSpellsLockSpell SpellsManager: not found spell type '{}'".format(self.spell_type))
                pass
            pass

    def __macroCompleteFilter(self, caller, *args):
        if caller != self.notificator:
            return False

        if args[0] != self.spell_type:
            return False

        return True

    def _onGenerate(self, source):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(Notificator.onSpellMacroComplete, Filter=self.__macroCompleteFilter)
            parallel_1.addNotify(self.notificator, self.spell_type)