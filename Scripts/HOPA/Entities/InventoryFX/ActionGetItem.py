from Foundation.PolicyManager import PolicyManager
from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionGetItem(ActionDefault):
    def _onParams(self, params):
        super(ActionGetItem, self)._onParams(params)
        self.itemName = params[0]
        pass

    def _onCheck(self):
        return True

    def _onRun(self, source):
        EffectPolicy = PolicyManager.getPolicy("EffectInventoryGetInventoryItem", "TaskEffectInventoryAddInventoryItem")
        source.addTask(EffectPolicy, Inventory=self.Inventory, ItemName=self.ItemName)
        source.addNotify(Notificator.onItemEffectEnd, self.ItemName)
