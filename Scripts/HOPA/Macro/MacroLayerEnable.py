from HOPA.Macro.MacroCommand import MacroCommand


class MacroLayerEnable(MacroCommand):
    def _onValues(self, values):
        self.Name = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onCommandLayerEnable, self.Name, True)
        source.addTask("TaskSceneLayerGroupEnable", LayerName=self.Name, Value=True, SceneName=self.SceneName)
        pass

    pass
