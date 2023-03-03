from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias


class AliasSpellUsage(MixinObject, TaskAlias):

    def _onParams(self, params):
        super(AliasSpellUsage, self)._onParams(params)
        self.Spell = params.get("Spell")
        self.SpellCost = params.get("SpellCost")

    def _onGenerate(self, source):
        InteractiveType = self.Object.getType()

        source.addTask("TaskNotify", ID=Notificator.onSpellUseMacroBegin, Args=(self.Object, self.Spell))
        if InteractiveType == "ObjectZoom":
            source.addTask("TaskSpellOnZoom", Zoom=self.Object, Spell=self.Spell, SpellCost=self.SpellCost)

        elif InteractiveType == "ObjectItem":
            source.addTask("TaskSpellOnItem", Item=self.Object, Spell=self.Spell, SpellCost=self.SpellCost)

        elif InteractiveType == "ObjectSocket":
            source.addTask("TaskSpellOnSocket", Socket=self.Object, Spell=self.Spell, SpellCost=self.SpellCost)

        elif InteractiveType == "ObjectTransition":
            source.addTask("TaskSpellOnTransition", Transition=self.Object, Spell=self.Spell, SpellCost=self.SpellCost)

        else:
            source.addTask("TaskPrint", Value="AliasSpellUsage unknown object type")

        source.addTask("TaskSpellUse", Spell=self.Spell, SpellCost=self.SpellCost)
        source.addTask("TaskNotify", ID=Notificator.onSpellUseMacroEnd, Args=(self.Object, self.Spell))
        # source.addTask("TaskPrint", Value =  "MacroSpellUse complete")
