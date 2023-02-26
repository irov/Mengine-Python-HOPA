from HOPA.Macro.MacroCommand import MacroCommand

class MacroClose(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        self.ObjectsTypeFilter = ["ObjectTransition", "ObjectZoom"]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)
            ObjectType = Object.getType()

            if self.hasObject(Object.name) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.ObjectName, self.GroupName))
                pass

            if ObjectType not in self.ObjectsTypeFilter:
                self.initializeFailed("MacroClose: %s:%s invalid type" % (ObjectType, self.ObjectName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSetParam", ObjectName=self.ObjectName, Param="BlockOpen", Value=True)
        pass

    pass