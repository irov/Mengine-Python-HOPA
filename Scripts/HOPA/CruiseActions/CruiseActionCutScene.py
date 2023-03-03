from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction


class CruiseActionCutScene(CruiseAction):
    def _onAction(self):
        button = None
        if GroupManager.hasObject("CutScene_Interface", "Movie2Button_Next"):
            button = GroupManager.getObject("CutScene_Interface", "Movie2Button_Next")
        elif GroupManager.hasObject("CutScene_Interface", "Movie2Button_Skip"):
            button = GroupManager.getObject("CutScene_Interface", "Movie2Button_Skip")

        if TaskManager.existTaskChain("CruiseActionCutScene") is True:
            TaskManager.cancelTaskChain("CruiseActionCutScene")

        Position = button.getCurrentMovieSocketCenter() if button else (0.0, 0.0)
        with TaskManager.createTaskChain(Name="CruiseActionCutScene") as tc:
            tc.addTask("AliasCruiseControlAction", Position=Position, Object=button)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
