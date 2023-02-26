from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroFindMana(MacroCommand):
    def _onValues(self, values):
        self.MovieName = values[0]
        self.Value = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.hasObject(self.MovieName) is False:
                self.initializeFailed("MacroFindMana not found Object %s in group %s" % (self.MovieName, self.GroupName))
                pass

            if self.Value <= 0:
                self.initializeFailed("MacroFindMana initialize failed. Value must be positive. Current is %d" % (self.Value))
                pass
            pass

        self.Movie = GroupManager.getObject(self.GroupName, self.MovieName)
        pass

    def _onGenerate(self, source):
        def __filter(movie):
            if movie is self.Movie:
                return True
                pass
            return False
            pass

        Quest = self.addQuest(source, "FindMana", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Movie)
        with Quest as tc_quest:
            tc_quest.addTask("TaskNotify", ID=Notificator.onManaSearchBegin, Args=(self.Movie, self.Value))
            tc_quest.addTask("TaskListener", ID=Notificator.onManaFind, Filter=__filter)
            pass
        pass
    pass