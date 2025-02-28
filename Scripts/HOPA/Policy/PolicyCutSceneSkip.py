from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyCutSceneSkip(TaskAlias):
    def _onParams(self, params):
        super(PolicyCutSceneSkip, self)._onParams(params)

        self.CutSceneGroup = params.get("CutSceneGroup", "CutScene_Interface")
        self.CutSceneName = params.get("CutSceneName", None)
        pass

    def _onGenerate(self, source):
        TaskName = ''
        ButtonName = ''
        if GroupManager.hasObject(self.CutSceneGroup, "Movie2Button_Skip") is True:
            TaskName = 'TaskMovie2ButtonClick'
            ButtonName = 'Movie2Button_Skip'
            Button_Skip = GroupManager.getObject(self.CutSceneGroup, "Movie2Button_Skip")
            Button_Skip.setEnable(True)

        elif GroupManager.hasObject(self.CutSceneGroup, "Button_Skip") is True:
            TaskName = 'TaskButtonClick'
            ButtonName = 'Button_Skip'
            Button_Skip = GroupManager.getObject(self.CutSceneGroup, "Button_Skip")
            Button_Skip.setEnable(True)

        if GroupManager.hasObject(self.CutSceneGroup, "Movie2Button_Skip") is False and GroupManager.hasObject(self.CutSceneGroup, "Button_Skip") is False:
            source.addBlock()
            return False
            pass

        if TaskName == 'TaskMovie2ButtonClick':
            source.addTask(TaskName, GroupName=self.CutSceneGroup, Movie2ButtonName=ButtonName)
        elif TaskName == 'TaskButtonClick':
            source.addTask(TaskName, GroupName=self.CutSceneGroup, ButtonName=ButtonName)
