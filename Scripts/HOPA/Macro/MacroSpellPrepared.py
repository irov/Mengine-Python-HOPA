from HOPA.Entities.Spell.SpellManager import SpellManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroSpellPrepared(MacroCommand):
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
        source.addTask("TaskNotify", ID=Notificator.onSpellPrepared, Args=(self.SpellID,))
        pass

    pass
