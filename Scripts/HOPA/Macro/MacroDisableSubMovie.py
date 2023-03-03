from HOPA.Macro.MacroCommand import MacroCommand


class MacroDisableSubMovie(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) == 0:
                self.initializeFailed("Macro %s not add any param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ObjectName = values[0]

        self.Layers = []
        if len(values) > 1:
            self.Layers = values[1:]
            pass
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)

            if Object is None:
                self.initializeFailed("MacroDisableSubMovie not found Object %s in group %s" % (self.ObjectName, self.GroupName))
            elif self.hasObject(Object.name) is False:
                self.initializeFailed("MacroDisableSubMovie not found Object %s in group %s" % (Object.name, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        if len(self.Layers) > 0 and (ObjectType == "ObjectMovie"):
            for Layer in self.Layers:
                source.addTask("TaskAppendParam", Object=Object, Param="DisableLayers", Value=Layer)
                pass

            return
            pass

        if len(self.Layers) > 0 and (ObjectType == "ObjectMovie2"):
            for Layer in self.Layers:
                source.addTask("TaskAppendParam", Object=Object, Param="DisableSubMovies", Value=Layer)
                pass

            return
            pass
        pass
