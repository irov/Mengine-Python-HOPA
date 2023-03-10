from HOPA.Macro.MacroCommand import MacroCommand


class MacroBlockInteractive(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.hasObject(self.ObjectName) is False:
                self.initializeFailed("MacroBlockInteractive not found Object %s in group %s" % (self.ObjectName, self.GroupName))

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)

        source.addTask("TaskBlockInteractive", Object=Object, BlockInteractive=True)
