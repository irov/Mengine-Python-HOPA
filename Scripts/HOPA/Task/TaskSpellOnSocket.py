from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.Entities.Spell.SystemSpell import SystemSpell


class TaskSpellOnSocket(MixinSocket, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskSpellOnSocket, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")
        pass

    def _onInitialize(self):
        super(TaskSpellOnSocket, self)._onInitialize()
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)
            pass
        self.addObserverFilter(Notificator.onSocketClickBegin, self.__onSocketFilter, self.Socket)
        return False
        pass

    def _onFinally(self):
        super(TaskSpellOnSocket, self)._onFinally()

        if self.AutoEnable is True:
            self.Socket.setInteractive(False)
            pass
        pass

    def __onSocketFilter(self, socket):
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
