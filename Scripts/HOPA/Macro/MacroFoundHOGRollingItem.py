from HOPA.HOGManager import HOGManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroFoundHOGRollingItem(MacroCommand):
    def _onValues(self, values):
        self.HOGName = values[0]
        self.HOGItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            hogItem = HOGManager.getHOGItem(self.HOGName, self.HOGItemName)
            objectName = hogItem.objectName
            if objectName is not None:
                self.initializeFailed("Item '%s' has objectName in hog %s xlsx, and found to this item generate automatically, please remove him from there" % (self.HOGItemName, self.HOGName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        ObjectHOG = HOGManager.getHOGObject(self.HOGName)

        source.addTask("AliasHOGRollingFoundItem", HOG=ObjectHOG, HOGItemName=self.HOGItemName, EnigmaName=self.HOGName)
        pass
    pass