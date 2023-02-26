from HOPA.Macro.MacroCommand import MacroCommand

class MacroMovieInterrupt(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            Filter = ["ObjectMovie"]

            if self.hasObject(self.ObjectName, Filter) is False:
                self.initializeFailed("MacroPlay not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)

        source.addTask("TaskMovieInterrupt", Movie=Object)
        pass
    pass