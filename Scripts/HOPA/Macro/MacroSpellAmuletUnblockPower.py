from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager, SPELL_AMULET_TYPE


class MacroSpellAmuletUnblockPower(MacroCommand):
    def _onValues(self, values):
        values_num = len(values)

        self.power_name = values[0]
        self.open = False

        if values_num > 1:
            self.open = bool(values[1])

        self.notificator = Notificator.onSpellAmuletUnblockPower

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellsManager.getSpellAmuletPowerParam(self.power_name) is None:
                self.initializeFailed("MacroSpellAmuletUnblockPower SpellsManager: not found power '{}'".format(self.power_name))
                pass
            pass

    def __macroCompleteFilter(self, caller, *args):
        if caller != self.notificator:
            return False

        if args[0] != self.power_name:
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
            parallel_1.addNotify(self.notificator, self.power_name, self.open)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(notificator_complete, Filter=self.__spellUIAmuletUpdateComplete)
            parallel_1.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE)
