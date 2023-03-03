from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemGamePause(System):
    PAUSE_GROUP = "GamePause"  # in same layer
    CONTINUE_BUTTON = "Button_Continue"
    TASK_NAME = "SystemGamePause_onPause"

    def __init__(self):
        super(SystemGamePause, self).__init__()
        self.FocusHandler = None
        self.onSceneEnterBreakHandler = None
        self.ButtonContinue = None
        self.Mute = None
        pass

    def _onRun(self):
        self.addObserver(Notificator.onFocus, self.on_focus_cb)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)

        if GroupManager.hasObject(SystemGamePause.PAUSE_GROUP, SystemGamePause.CONTINUE_BUTTON):
            self.ButtonContinue = GroupManager.getObject(SystemGamePause.PAUSE_GROUP, SystemGamePause.CONTINUE_BUTTON)
        else:
            Trace.log("System", 0, "%s or %s doesn exists" % button_path)

        return True
        pass

    def _onStop(self):
        self.ButtonContinue = None
        pass

    def freezeCurrentScene(self, freeze):
        SceneName = SceneManager.getCurrentSceneName()
        Groups = SceneManager.getSceneLayerGroups(SceneName)

        GroupPauseGroup = SceneManager.getSceneLayerGroup(SceneName, SystemGamePause.PAUSE_GROUP)

        for Group in Groups:
            if Group is GroupPauseGroup:
                continue
                pass  # print "Freeze GroupName %s:%s"%(Group.getName(), SystemGamePause.PAUSE_GROUP)

            Scene = Group.getScene()
            Scene.freeze(freeze)
            pass

        if freeze is True:
            Mute = Mengine.isMute()
            if Mute is True:
                return
                pass

            self.Mute = True
            Mengine.soundMute(True)
            pass
        else:
            if self.Mute is None:
                return
                pass

            Mengine.soundMute(False)
            self.Mute = None
            pass

        pass

    def on_focus_cb(self, focus):
        if focus is True:
            return False
            pass

        currentScene = SceneManager.getCurrentScene()
        if currentScene is None:
            return False
            pass

        if SceneManager.hasLayerScene(SystemGamePause.PAUSE_GROUP) is False:
            return False
            pass

        if TaskManager.existTaskChain(SystemGamePause.TASK_NAME):
            return False
            pass

        with TaskManager.createTaskChain(Name=SystemGamePause.TASK_NAME) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName=SystemGamePause.PAUSE_GROUP, Value=True)

            tc.addTask("TaskFunction", Fn=self.freezeCurrentScene, Args=(True,))

            tc.addTask("TaskButtonClick", Button=self.ButtonContinue)

            tc.addTask("TaskFunction", Fn=self.freezeCurrentScene, Args=(False,))

            tc.addTask("TaskSceneLayerGroupEnable", LayerName=SystemGamePause.PAUSE_GROUP, Value=False)
            pass

        return False
        pass

    def __onSceneLeave(self, scene):
        if TaskManager.existTaskChain(SystemGamePause.TASK_NAME):
            TaskManager.cancelTaskChain(SystemGamePause.TASK_NAME)

            with TaskManager.createTaskChain(Name=SystemGamePause.TASK_NAME) as tc:
                tc.addTask("TaskFunction", Fn=self.freezeCurrentScene, Args=(False,))
                tc.addTask("TaskSceneLayerGroupEnable", LayerName=SystemGamePause.PAUSE_GROUP, Value=False)
                pass
            pass

        return False
