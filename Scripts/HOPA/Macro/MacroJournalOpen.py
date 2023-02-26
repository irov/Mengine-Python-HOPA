from HOPA.Macro.MacroCommand import MacroCommand

class MacroJournalOpen(MacroCommand):
    def _onValues(self, values):
        if len(values) < 1:
            return
            pass
        self.layerName = values[0]
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSceneLayerGroupEnable", LayerName=self.layerName, Value=True)
        pass
    pass