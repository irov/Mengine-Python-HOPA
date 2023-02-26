from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager, SPELL_AMULET_TYPE
from HOPA.System.SystemSpells import SystemSpells

class MacroSpellAmuletUsePower(MacroCommand):

    def _onValues(self, values):
        self.power_name = values[0]
        self.open = bool(values[1]) if len(values) > 1 else False

        power_params = SpellsManager.getSpellAmuletPowerParam(self.power_name)
        self.power_type = power_params.power_type

        self.notificator = Notificator.onSpellAmuletUsePower

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellsManager.getSpellAmuletPowerParam(self.power_name) is None:
                self.initializeFailed("MacroSpellAmuletUsePower SpellsManager: not found power '{}'".format(self.power_name))
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

    def __runQuest(self, source):
        quest_type = SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE).spell_use_quest
        quest = self.addQuest(source, quest_type, SceneName=self.SceneName, GroupName=self.GroupName, PowerName=self.power_name)

        source.addNotify(self.notificator, self.power_name, self.open, self.ScenarioQuests[-1])

        with quest as tc_quest:
            with tc_quest.addParallelTask(2) as (parallel_0, parallel_1):
                parallel_0.addListener(Notificator.onSpellMacroComplete, Filter=self.__macroCompleteFilter)
                parallel_1.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE)  # for state ready

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addListener(Notificator.onSpellMacroComplete, Filter=self.__spellUIAmuletUpdateComplete)
            parallel_1.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE, updateStatePlay=False)

    def __isRuneLocked(self):
        rune = SystemSpells.getSpellAmuletStoneByPower(self.power_name)
        return rune.locked

    def _onGenerate(self, source):
        with source.addIfTask(self.__isRuneLocked) as (wait, _):
            wait.addListener(Notificator.onSpellAmuletAddPower, Filter=lambda power_type, *args: power_type == self.power_type)

        source.addScope(self.__runQuest)