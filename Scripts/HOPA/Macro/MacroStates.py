from HOPA.Macro.MacroCommand import MacroCommand

class MacroStates(MacroCommand):
    def __init__(self):
        super(MacroStates, self).__init__()

        self.States = None
        pass

    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 2:
                self.initializeFailed("Macr o%s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.StatesName = values[0]
        self.Value = values[1]
        pass

    def _onInitialize(self):
        Filter = ["ObjectStates"]

        if _DEVELOPMENT is True:
            if self.hasObject(self.StatesName, Filter) is False:
                self.initializeFailed("States not found Object %s in group %s" % (self.StatesName, self.GroupName))
                pass
            pass

        FinderType, self.States = self.findObject(self.StatesName, Filter)

        if _DEVELOPMENT is True:
            if self.States.hasState(self.Value) is False:
                self.initializeFailed("States %s not found value %s" % (self.StatesName, self.Value))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskStates", States=self.States, Value=self.Value)
        pass
    pass