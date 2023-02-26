from HOPA.HOGManager import HOGManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroFoundHOGItem(MacroCommand):
    def _onValues(self, values):
        self.HOGName = values[0]
        self.HOGItemName = values[1]
        pass

    def _onGenerate(self, source):
        ObjectHOG = HOGManager.getHOGObject(self.HOGName)

        source.addTask("AliasHOGFoundItem", HOG=ObjectHOG, HOGItemName=self.HOGItemName, EnigmaName=self.HOGName)
        source.addTask("TaskHOGComplete", HOG=ObjectHOG)
        pass
    pass