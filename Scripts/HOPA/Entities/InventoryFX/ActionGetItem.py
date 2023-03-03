from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionGetItem(ActionDefault):
    def _onParams(self, params):
        super(ActionGetItem, self)._onParams(params)
        self.itemName = params[0]
        pass

    def _onCheck(self):
        return True

    def _onSkip(self):
        if TaskManager.existTaskChain("InvFXActionGetItem%s" % self.ItemName):
            TaskManager.cancelTaskChain("InvFXActionGetItem%s" % self.ItemName)

    def _onRun(self):
        EffectPolicy = PolicyManager.getPolicy("EffectInventoryGetInventoryItem", "TaskEffectInventoryAddInventoryItem")
        with TaskManager.createTaskChain(Name="InvFXActionGetItem%s" % self.ItemName, Cb=self.endItem) as tc:
            tc.addTask(EffectPolicy, Inventory=self.Inventory, ItemName=self.ItemName)
            tc.addTask("TaskNotify", ID=Notificator.onItemEffectEnd, Args=(self.ItemName,))
