from Foundation.System import System
from Foundation.TaskManager import TaskManager

class SystemBonusGameComplete(System):
    def __init__(self):
        super(SystemBonusGameComplete, self).__init__()
        pass

    # def _onSave(self, save):
    #   save["SystemBonusGameComplete"] = self.isComplete
    #  pass

    # def _onLoad(self, save):
    #   self.isComplete = save["SystemBonusGameComplete"]
    #  pass

    def _onRun(self):
        self.addObserver(Notificator.onBonusGameComplete, self.__onBonusGameComplete)
        self.addObserver(Notificator.onGameComplete, self.__onGameComplete)

        return True
        pass

    def __onGameComplete(self):
        self._gameComplete()
        return True
        pass

    def _gameComplete(self):
        if TaskManager.existTaskChain("GameCompleteMessage") is True:
            TaskManager.cancelTaskChain("GameCompleteMessage")
            pass

        with TaskManager.createTaskChain(Name="GameCompleteMessage") as tc:
            tc.addTask("TaskSceneEnter", SceneName="Menu")
            tc.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=0.25 * 1000)  # speed fix
            tc.addTask("AliasMessageOKShow", TextID="ID_GAME_COMPLETE")
            tc.addTask("TaskButtonClick", GroupName="MessageOK", ButtonName="Button_OK")
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="MessageOK", Value=False)
            tc.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=0.25 * 1000, From=0.5)  # speed fix
            pass
        pass

    def __onBonusGameComplete(self):
        self._onComplete()
        return True
        pass

    def _onComplete(self):
        with TaskManager.createTaskChain(Name="MenuBonusComplete", GroupName="MenuBackground") as tc:
            tc.addTask("TaskSceneEnter", SceneName="Menu")
            tc.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=0.25 * 1000)  # speed fix
            tc.addTask("AliasMessageOKShow", TextID="ID_BONUS_GAME_COMPLETE")
            tc.addTask("TaskButtonClick", GroupName="MessageOK", ButtonName="Button_OK")
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="MessageOK", Value=False)
            tc.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=0.25 * 1000, From=0.5)  # speed fix
            pass
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("MenuBonusComplete") is True:
            TaskManager.cancelTaskChain("MenuBonusComplete")
            pass

        if TaskManager.existTaskChain("GameCompleteMessage") is True:
            TaskManager.cancelTaskChain("GameCompleteMessage")
            pass
        pass
    pass