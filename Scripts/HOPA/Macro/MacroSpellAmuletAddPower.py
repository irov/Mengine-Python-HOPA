from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager, SPELL_AMULET_TYPE

class MacroSpellAmuletAddPower(MacroCommand):
    def _onValues(self, values):
        values_num = len(values)

        self.power_type = values[0]
        self.open = bool(values[1]) if values_num > 1 else False
        self.close_after_open = bool(values[2]) if values_num > 2 else False

        self.notificator = Notificator.onSpellAmuletAddPower

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellsManager.getSpellAmuletStoneParam(self.power_type) is None:
                self.initializeFailed("MacroSpellAmuletAddPower SpellsManager: not found power type '{}'".format(self.power_type))

    def __macroCompleteFilter(self, caller, *args):
        if caller != self.notificator:
            return False

        if args[0] != self.power_type:
            return False

        return True

    @staticmethod
    def __spellUIAmuletUpdateComplete(caller, *args):
        if caller != Notificator.onSpellUISpellUpdate:
            return False

        if args[0] != SPELL_AMULET_TYPE:
            return False

        return True

    def _onGenerate(self, source):
        notificator_complete = Notificator.onSpellMacroComplete

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(notificator_complete, Filter=self.__macroCompleteFilter)
            parallel_1.addNotify(self.notificator, self.power_type, self.open, self.close_after_open)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(notificator_complete, Filter=self.__spellUIAmuletUpdateComplete)
            parallel_1.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE)