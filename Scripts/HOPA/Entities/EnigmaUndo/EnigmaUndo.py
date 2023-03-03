from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager


class EnigmaUndo(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def __init__(self):
        super(EnigmaUndo, self).__init__()

    def _onActivate(self):
        with TaskManager.createTaskChain(Name="EnigmaUndo", Repeat=True) as tc:
            tc.addTask("TaskButtonClick", Group=self.object, ButtonName="Button_Undo")
            tc.addTask("TaskNotify", ID=Notificator.onEnigmaUndoStep)

    def onDeactivate(self):
        if TaskManager.existTaskChain("EnigmaUndo"):
            TaskManager.cancelTaskChain("EnigmaUndo")
