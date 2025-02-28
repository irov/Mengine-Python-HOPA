from HOPA.Macro.MacroCommand import MacroCommand


class MacroLayerDisable(MacroCommand):
    def _onValues(self, values):
        self.Name = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onCommandLayerEnable, self.Name, False)
        source.addTask("TaskSceneLayerGroupEnable", LayerName=self.Name, Value=False, SceneName=self.SceneName)
        pass

    pass
