from HOPA.Macro.MacroCommand import MacroCommand

class MacroShift(MacroCommand):
    def __init__(self):
        super(MacroShift, self).__init__()

        self.Shift = None
        pass

    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) < 2:
                self.initializeFailed("Macro %s not add all param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ShiftName = values[0]
        self.Value = values[1]
        pass

    def _onInitialize(self):
        Filter = ["ObjectShift"]

        if _DEVELOPMENT is True:
            if self.hasObject(self.ShiftName, Filter) is False:
                self.initializeFailed("Shift not found Object %s in group %s" % (self.ShiftName, self.GroupName))
                pass
            pass

        FinderType, self.Shift = self.findObject(self.ShiftName, Filter)

        if _DEVELOPMENT is True:
            if self.Shift.hasShift(self.Value) is False:
                self.initializeFailed("Shift %s not found value %s" % (self.ShiftName, self.Value))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskShift", Shift=self.Shift, Value=self.Value)
        pass
    pass