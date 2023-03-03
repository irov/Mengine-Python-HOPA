from HOPA.Macro.MacroCommand import MacroCommand


class MacroMousePull(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        self.MovieName = values[1]
        self.Direction = values[2]
        self.MovieWrongName = values[3]

        self.Distance = 100
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.hasObject(self.ObjectName) is False:
                self.initializeFailed("MacroMousePull not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass

            if self.hasObject(self.MovieName) is False:
                self.initializeFailed("MacroMousePull not found Movie %s in group %s" % (self.SocketName, self.GroupName))
                pass

            if self.hasObject(self.MovieWrongName) is False:
                self.initializeFailed("MacroMousePull not found TransformMovie %s in group %s" % (self.MovieWrongName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Pull", SceneName=self.SceneName, GroupName=self.GroupName,
                              ObjectName=self.ObjectName, Direction=self.Direction)
        with Quest as tc:
            tc.addTask("AliasMousePull", ObjectName=self.ObjectName, MovieName=self.MovieName,
                       MovieWrongName=self.MovieWrongName, Direction=self.Direction, Distance=self.Distance)

            pass
        pass
