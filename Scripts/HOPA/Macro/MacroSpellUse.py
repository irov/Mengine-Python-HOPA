from Foundation.GroupManager import GroupManager
from HOPA.Entities.Spell.SpellManager import SpellManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroSpellUse(MacroCommand):
    def _onValues(self, values):
        self.SpellID = values[0]
        self.ObjectName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SpellManager.hasSpellObject(self.SpellID) is False:
                self.initializeFailed("Can't find SpellID name %s " % (self.SpellID,))
                pass
            if GroupManager.hasObject(self.GroupName, self.ObjectName) is False:
                self.initializeFailed("Can't find  %s on %s " % (self.ObjectName, self.GroupName))
                pass
            pass

        self.Object = GroupManager.getObject(self.GroupName, self.ObjectName)
        self.Spell = SpellManager.getSpellObject(self.SpellID)
        self.SpellCost = None

        if SpellManager.hasSpellCost(self.SpellID) is True:
            self.SpellCost = SpellManager.getSpellCost(self.SpellID)
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "SpellUse", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Object, Spell=self.Spell)
        with Quest as tc_q:
            tc_q.addTask("AliasSpellUsage", Object=self.Object, Spell=self.Spell, SpellCost=self.SpellCost)
            pass
        pass