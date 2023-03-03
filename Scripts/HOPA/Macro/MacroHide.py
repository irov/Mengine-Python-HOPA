from HOPA.Macro.MacroCommand import MacroCommand


class MacroHide(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        # self.ObjectTypeFilter = ["ObjectSocket", "ObjectZoom", "ObjectTransition", "ObjectItem"]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)

            if self.hasObject(Object.name) is False:
                self.initializeFailed("MacroHide not found Object %s in group %s" % (Object.name, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        # FinderType, Object = self.findObject(self.ObjectName)
        # ObjectType = Object.getType()
        source.addTask("AliasObjectAlphaTo", ObjectName=self.ObjectName, From=1.0, To=0.5, Time=3000)
        pass

    pass
