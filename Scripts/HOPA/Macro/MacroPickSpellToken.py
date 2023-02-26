from HOPA.Entities.Spell.SpellManager import SpellManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroPickSpellToken(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        self.SpellID = values[1]
        pass

    def _onInitialize(self):
        FinderType, self.Item = self.findObject(self.ItemName)

        if _DEVELOPMENT is True:
            if self.Item is None:
                self.initializeFailed("Not found current item %s with this group %s in ItemManager" % (self.ItemName, self.GroupName))
                pass

            if self.hasObject(self.Item.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.Item.name, self.GroupName))
                pass

            if SpellManager.hasSpellObject(self.SpellID) is False:
                self.initializeFailed("Can't find SpellID name %s " % (self.SpellID,))
                pass
            pass

        self.Spell = SpellManager.getSpellObject(self.SpellID)
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Click", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Item)
        with Quest as tc_quest:
            tc_quest.addTask("TaskItemClick", Item=self.Item)
            tc_quest.addTask("TaskItemPick", Item=self.Item)
            tc_quest.addTask("AliasPickSpellTokenEffect", Item=self.Item, Spell=self.Spell)
            tc_quest.addTask("TaskNotify", ID=Notificator.onSpellReady, Args=(self.SpellID,))
            pass
        pass

    pass