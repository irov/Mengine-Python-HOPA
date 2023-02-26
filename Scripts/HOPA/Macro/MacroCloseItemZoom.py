from HOPA.Macro.MacroCommand import MacroCommand

class MacroCloseItemZoom(MacroCommand):
    def _onValues(self, values, **params):
        pass

    def _onInitialize(self, **params):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onItemZoomLeaveOpenZoom)
        pass
    pass