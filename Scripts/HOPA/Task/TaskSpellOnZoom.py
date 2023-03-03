from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinZoom
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.Entities.Spell.SystemSpell import SystemSpell


class TaskSpellOnZoom(MixinZoom, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskSpellOnZoom, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")
        pass

    def _onInitialize(self):
        super(TaskSpellOnZoom, self)._onInitialize()
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Zoom.setInteractive(True)
            pass
        self.addObserverFilter(Notificator.onZoomClickBegin, self._onZoomClickFilter, self.Zoom)

        return False
        pass

    def _onFinally(self):
        super(TaskSpellOnZoom, self)._onFinally()

        if self.AutoEnable is True:
            self.Zoom.setInteractive(False)
            pass
        pass

    def _onZoomClickFilter(self, zoom):
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
