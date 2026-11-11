from Foundation.PolicyManager import PolicyManager
from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionPickItem(ActionDefault):
    def _onCheck(self):
        return True
        pass

    def _onRun(self, source):
        EffectPolicy = PolicyManager.getPolicy("EffectInventoryAddInventoryItem", "TaskEffectInventoryAddInventoryItem")

        # source.addPrint("ActionPickItem")
        source.addTask(EffectPolicy, Inventory=self.Inventory, ItemName=self.ItemName)
        source.addNotify(Notificator.onItemEffectEnd, self.ItemName)
