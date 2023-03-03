from HOPA.Entities.Spell.SpellManager import SpellManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroEnvSpellUse(MacroCommand):
    def _onValues(self, values):
        self.SpellID = values[0]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellManager.hasSpellObject(self.SpellID) is False:
                self.initializeFailed("Can't find SpellID name %s " % (self.SpellID,))

        self.Spell = SpellManager.getSpellObject(self.SpellID)
        self.SpellCost = None
        if SpellManager.hasSpellCost(self.SpellID) is True:
            self.SpellCost = SpellManager.getSpellCost(self.SpellID)

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "EnvSpellUse", SceneName=self.SceneName,
                              GroupName=self.GroupName, Spell=self.Spell)
        with Quest as tc_q:
            tc_q.addTask("TaskSpellUse", Spell=self.Spell, SpellCost=self.SpellCost)
            tc_q.addTask("TaskPrint", Value="TaskSpellUse complete")
