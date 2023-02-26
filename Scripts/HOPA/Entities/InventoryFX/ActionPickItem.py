from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault

class ActionPickItem(ActionDefault):
    def _onCheck(self):
        return True
        pass

    def _onSkip(self):
        if TaskManager.existTaskChain("InvFXActionPickItem%s" % self.ItemName):
            TaskManager.cancelTaskChain("InvFXActionPickItem%s" % self.ItemName)
            pass
        pass

    def _onRun(self):
        EffectPolicy = PolicyManager.getPolicy("EffectInventoryAddInventoryItem", "TaskEffectInventoryAddInventoryItem")

        with TaskManager.createTaskChain(Name="InvFXActionPickItem%s" % self.ItemName, Cb=self.endItem) as tc:
            # tc.addPrint("ActionPickItem")
            tc.addTask(EffectPolicy, Inventory=self.Inventory, ItemName=self.ItemName)
            tc.addTask("TaskNotify", ID=Notificator.onItemEffectEnd, Args=(self.ItemName,))

            pass
        pass
    pass