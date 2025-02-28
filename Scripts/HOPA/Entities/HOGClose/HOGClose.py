from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager


class HOGClose(BaseEntity):
    def __init__(self):
        super(HOGClose, self).__init__()
        pass

    def _onActivate(self):
        currentHogSceneName = SceneManager.getCurrentSceneName()
        with TaskManager.createTaskChain(Name="HOGCloseClick", Group=self.object) as tc:
            tc.addTask("TaskButtonClick", ButtonName="Button_CloseHOG")
            tc.addNotify(Notificator.onHOGCloseClick, currentHogSceneName)
            pass
        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("HOGCloseClick"):
            TaskManager.cancelTaskChain("HOGCloseClick")
