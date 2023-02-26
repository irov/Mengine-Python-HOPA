from HOPA.Macro.MacroCommand import MacroCommand

class MacroUnblockInteractive(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.hasObject(self.ObjectName) is False:
                self.initializeFailed("MacroUnblockInteractive not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)

        source.addTask("TaskBlockInteractive", Object=Object, BlockInteractive=False)
        pass
    pass