from HOPA.Macro.MacroCommand import MacroCommand


class MacroStop(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            Filter = ["ObjectMovie", "ObjectEffect", "ObjectAnimation", "ObjectMovie2"]

            if self.hasObject(self.ObjectName, Filter) is False:
                self.initializeFailed("MacroStop not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        if ObjectType == "ObjectMovie":
            source.addTask("TaskMovieStop", Movie=Object)
        elif ObjectType == "ObjectMovie2":
            source.addTask("TaskMovie2Stop", Movie2=Object)
            pass
        pass

    pass
