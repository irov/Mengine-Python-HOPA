from HOPA.HOGManager import HOGManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGItemActivate(MacroCommand):
    def _onValues(self, values):
        self.HOGName = values[0]
        self.HOGItemName = values[1]
        pass

    def _onGenerate(self, source):
        hogItemData = HOGManager.getHOGItem(self.HOGName, self.HOGItemName)
        source.addTask("TaskFunction", Fn=hogItemData.setActivate, Args=(True,))
        pass

    pass
