from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from Notification import Notification


class SystemStrategyGuideButton(System):
    def __init__(self):
        super(SystemStrategyGuideButton, self).__init__()
        self.isGuideMenu = True
        self.SceneInitObserver = None
        self.onLayerGroupPreparationObserver = None
        pass

    def _onSave(self):
        return self.isGuideMenu
        pass

    def _onLoad(self, data_save):
        self.isGuideMenu = data_save
        pass

    def setIsGuideMenu(self, value):
        self.isGuideMenu = value
        pass

    def _onRun(self):
        self.SceneInitObserver = Notification.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.runTaskChain()
        return True
        pass

    def __onSceneInit(self, sceneName):
        if SceneManager.hasLayerScene("StrategyGuideButton") is False:
            return False
            pass
        TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="StrategyGuideButton")
        return False
        pass

    def runTaskChain(self):
        def __isGuideMenu(isSkip, cb):
            if self.isGuideMenu is True:
                cb(isSkip, 0)
                return
                pass
            elif self.isGuideMenu is False:
                cb(isSkip, 1)
                return
                pass
            cb(isSkip, 0)
            return
            pass

        with TaskManager.createTaskChain(Name="StrategyGuideButtonMove", Repeat=True) as tc:
            tc.addTask("TaskButtonClick", GroupName="StrategyGuideButton", ButtonName="MovieButton_StrategyGuide")
            with tc.addSwitchTask(2, __isGuideMenu) as (tc_menu, tc_guide):
                tc_menu.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideMenu")

                tc_guide.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuidePages")
                tc_guide.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideZoom")
                pass
            pass
        pass

    def _onStop(self):
        Notification.removeObserver(self.SceneInitObserver)
        self.SceneInitObserver = None

        if TaskManager.existTaskChain("StrategyGuideButtonMove") is True:
            TaskManager.cancelTaskChain("StrategyGuideButtonMove")
