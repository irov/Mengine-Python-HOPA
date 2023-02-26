from HOPA.Macro.MacroCommand import MacroCommand

class MacroPuffDel(MacroCommand):
    def __init__(self):
        super(MacroPuffDel, self).__init__()

        self.Puff = None
        pass

    def _onValues(self, values):
        self.PuffName = values[0]
        self.Value = values[1]
        pass

    def _onInitialize(self):
        Filter = ["ObjectPuff"]

        if _DEVELOPMENT is True:
            if self.hasObject(self.PuffName, Filter) is False:
                self.initializeFailed("Puff not found Object %s in group %s" % (self.PuffName, self.GroupName))
                pass
            pass

        FinderType, self.Puff = self.findObject(self.PuffName, Filter)

        if _DEVELOPMENT is True:
            if self.Puff.hasElement(self.Value) is False:
                self.initializeFailed("Puff %s not found value %s" % (self.PuffName, self.Value))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskPuffShowElement", Puff=self.Puff, ElementName=self.Value, Enable=False)
        pass
    pass