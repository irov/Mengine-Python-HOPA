from HOPA.Macro.MacroCommand import MacroCommand

class MacroMovieLayerSetEnable(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]

        self.LayerName = values[1]

        self.Enable = bool(values[2])

        self.Object = self.findObject(self.ObjectName)[1]

    def _onGenerate(self, source):
        if self.Object is not None and self.LayerName is not None:
            if self.Enable:
                if self.LayerName in self.Object.getParam('DisableLayers'):
                    source.addFunction(self.Object.delParam, "DisableLayers", self.LayerName)

            else:
                if self.LayerName not in self.Object.getParam('DisableLayers'):
                    source.addFunction(self.Object.appendParam, "DisableLayers", self.LayerName)