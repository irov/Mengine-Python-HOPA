from Foundation.PolicyManager import PolicyManager
from HOPA.HOGManager import HOGManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGFoundHOGItem(MacroCommand):
    def _onValues(self, values):
        self.HOGName = values[0]
        self.HOGItemName = values[1]

    def _onGenerate(self, source):
        ObjectHOG = HOGManager.getHOGObject(self.HOGName)
        HOGInventory = HOGManager.getInventory(self.HOGName)

        if HOGInventory.getType() == 'ObjectHOGInventoryRolling':
            PolicyDeleteItemFromInventory = PolicyManager.getPolicy("HOGRollingDeleteItemFromInventory", "PolicyDeleteItemFromInventory")

            source.addTask("TaskNotify", ID=Notificator.onHOGFoundItem, Args=(self.HOGItemName,))
            source.addTask(PolicyDeleteItemFromInventory, HOG=ObjectHOG, HOGItemName=self.HOGItemName, EnigmaName=self.HOGName)

        source.addTask("TaskHOGFoundItem", HOG=ObjectHOG, HOGItemName=self.HOGItemName)