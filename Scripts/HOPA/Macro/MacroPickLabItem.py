from HOPA.Macro.MacroCommand import MacroCommand


class MacroPickLabItem(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
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
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Click", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Item)
        with Quest as tc_quest:
            tc_quest.addTask("TaskItemClick", Item=self.Item)
            tc_quest.addTask("TaskItemPick", Item=self.Item)
            tc_quest.addTask("AliasPickLabItemEffect", Item=self.Item)
            tc_quest.addNotify(Notificator.onPickLabItem)
            pass
        pass

    pass
