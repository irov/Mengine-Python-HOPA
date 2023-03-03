from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.Entities.Spell.SystemSpell import SystemSpell


class TaskSpellOnItem(MixinItem, MixinObserver, Task):

    def _onParams(self, params):
        super(TaskSpellOnItem, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")
        pass

    def _onInitialize(self):
        super(TaskSpellOnItem, self)._onInitialize()
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Item.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onItemClickBegin, self._onItemFindFilter, self.Item)
        return False
        pass

    def _onFinally(self):
        super(TaskSpellOnItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Item.setInteractive(False)
            pass
        pass

    def _onItemFindFilter(self, item):
        if self.Spell == SystemSpell.getCurrentSpell():
            self.Spell.setIsValidUse(True)
            if self.SpellCost is None:
                return True
            else:
                Mana = DemonManager.getDemon("Mana")
                Value = Mana.getManaCount()
                if Value >= self.SpellCost:
                    return True
                else:
                    return False
        return False
