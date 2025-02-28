from HOPA.Entities.Spell.SpellManager import SpellManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroSpellReady(MacroCommand):
    def _onValues(self, values):
        self.SpellID = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellManager.hasSpellObject(self.SpellID) is False:
                self.initializeFailed("Spell %s is not define" % (self.SpellID,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "SpellReady", SceneName=self.SceneName, GroupName=self.GroupName,
                              SpellID=self.SpellID)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onSpellReady, self.SpellID)
            pass
        pass

    pass
