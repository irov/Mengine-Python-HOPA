from HOPA.Macro.MacroCommand import MacroCommand

class MacroCollectedMapAdd(MacroCommand):
    def _onValues(self, values):
        self.PartName = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onCollectedMapAddPart, Args=(self.PartName,))
        pass

    pass