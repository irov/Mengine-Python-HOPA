from Foundation.GroupManager import GroupManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemObjectiveShow(System):
    def __init__(self):
        super(SystemObjectiveShow, self).__init__()
        pass

    def _onRun(self):
        socketObjective = GroupManager.getObject("Objectives", "Socket_Objective")

        with TaskManager.createTaskChain(Name="ButtonObjectiveClick", GroupName="Objectives", Repeat=True) as tc:
            tc.addTask("TaskSocketClick", Socket=socketObjective)
            tc.addTask("TaskNotify", ID=Notificator.onObjectiveShow)
            with tc.addRaceTask(2) as (tc_click, tc_delay):
                tc_click.addTask("TaskSocketClick", Socket=socketObjective)
                tc_delay.addTask("TaskDelay", Time=10 * 1000)  # speed fix
                pass
            tc.addTask("TaskNotify", ID=Notificator.onObjectiveHide)
            pass

            pass
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("ButtonObjectiveClick"):
            TaskManager.cancelTaskChain("ButtonObjectiveClick")
            pass
        pass
