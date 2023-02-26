from HOPA.Macro.MacroCommand import MacroCommand

class MacroMovieRewind(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            Filter = ["ObjectMovie", "ObjectMovie2"]

            if self.hasObject(self.ObjectName, Filter) is False:
                self.initializeFailed("MacroPlay not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        # source.addTask("TaskPrint", Value = "MacroPlay")
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        source.addTask("TaskMovieRewind", Movie=Object)

        pass
    pass