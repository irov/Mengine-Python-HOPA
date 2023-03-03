from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionHintUse(ActionDefault):

    def _onCheck(self):
        return True
        pass

    def _onRun(self):
        with TaskManager.createTaskChain(Cb=self.endItem) as tc:
            tc.addTask("TaskNotify", ID=Notificator.onItemEffectEnd, Args=(self.ItemName,))
