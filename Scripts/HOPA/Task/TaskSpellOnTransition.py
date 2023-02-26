from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.Entities.Spell.SystemSpell import SystemSpell

class TaskSpellOnTransition(MixinTransition, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskSpellOnTransition, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")
        pass

    def _onInitialize(self):
        super(TaskSpellOnTransition, self)._onInitialize()
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Transition.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onTransitionClickBegin, self.__onTransitionFilter, self.Transition)
        return False
        pass

    def _onFinally(self):
        super(TaskSpellOnTransition, self)._onFinally()

        if self.AutoEnable is True:
            self.Transition.setInteractive(False)
            pass
        pass

    def __onTransitionFilter(self, Transition):
        if self.Spell == SystemSpell.getCurrentSpell():
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
            pass
        return False
        pass
    pass