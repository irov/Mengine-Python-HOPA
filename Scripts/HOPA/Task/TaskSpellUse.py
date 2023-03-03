from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskSpellUse(MixinObserver, Task):

    def _onParams(self, params):
        super(TaskSpellUse, self)._onParams(params)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")
        pass

    def _onInitialize(self):
        super(TaskSpellUse, self)._onInitialize()
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onSpellEndUse, self.__onBeginSpell, self.Spell)
        return False
        pass

    def __onBeginSpell(self, spellObject):
        self.Spell.setIsValidUse(True)
        if self.SpellCost is None:
            return True
        else:
            Mana = DemonManager.getDemon("Mana")
            Value = Mana.getManaCount()
            if Value >= self.SpellCost:
                return True
                pass
            else:
                return False
                pass
            pass
        return False
        pass

    pass
