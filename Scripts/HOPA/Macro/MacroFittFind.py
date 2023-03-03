from HOPA.Macro.MacroCommand import MacroCommand


class MacroFittFind(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]

    def _onGenerate(self, source):
        source.addTask("AliasFittingFindItem", SceneName=self.SceneName, ItemName=self.ItemName)
