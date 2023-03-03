from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyCutSceneNext(TaskAlias):
    def _onParams(self, params):
        super(PolicyCutSceneNext, self)._onParams(params)

        self.CutSceneGroup = params.get("CutSceneGroup", "CutScene_Interface")
        self.CutSceneName = params.get("CutSceneName", None)
        pass

    def _onGenerate(self, source):
        TaskName = ''
        ButtonName = ''
        if GroupManager.hasObject(self.CutSceneGroup, "Movie2Button_Next") is True:
            TaskName = 'TaskMovie2ButtonClick'
            ButtonName = 'Movie2Button_Next'
            Button_Skip_Name = ButtonName  # ?
            Button_Skip = GroupManager.getObject(self.CutSceneGroup, Button_Skip_Name)
            Button_Skip.setEnable(True)

        elif GroupManager.hasObject(self.CutSceneGroup, "Button_Next") is True:
            TaskName = 'TaskButtonClick'
            ButtonName = 'Button_Next'
            Button_Skip = GroupManager.getObject(self.CutSceneGroup, "Button_Next")
            Button_Skip.setEnable(True)

        if GroupManager.hasObject(self.CutSceneGroup, "Movie2Button_Next") is False and GroupManager.hasObject(self.CutSceneGroup, "Button_Next") is False:
            source.addTask("TaskDeadLock")
            return False

        if TaskName == 'TaskMovie2ButtonClick':
            source.addTask(TaskName, GroupName=self.CutSceneGroup, Movie2ButtonName=ButtonName)
        elif TaskName == 'TaskButtonClick':
            source.addTask(TaskName, GroupName=self.CutSceneGroup, ButtonName=ButtonName)
