from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.OverViewManager import OverViewManager


class MacroFindHiddenItem(MacroCommand):
    def _onValues(self, values):
        self.ViewID = values[0]
        self.HasID = True

    def _onInitialize(self):
        self.HasID = OverViewManager.hasView(self.ViewID)

        if _DEVELOPMENT is True:
            if self.HasID is False:
                self.initializeFailed("MacroFindHiddenItem %s not found" % (self.ViewID))

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "FindHiddenItem", SceneName=self.SceneName, GroupName=self.GroupName)
        with Quest as tc_quest:
            tc_quest.addTask("AliasOverViewPlay", ObjectName=self.ViewID, ViewID=self.ViewID)
            tc_quest.addTask("TaskListener", ID=Notificator.OnOverViewShowed, Filter=self._rightViewID)

    def _rightViewID(self, viewID):
        if (viewID == self.ViewID):
            return True
        return False
