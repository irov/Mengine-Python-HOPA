from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskScenePlusInit(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskScenePlusInit, self)._onParams(params)

        self.SceneName = params.get("SceneName", None)
        self.SceneAny = params.get("SceneAny", False)
        pass

    def _onInitialize(self):
        super(TaskScenePlusInit, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.SceneAny is False:
                if self.SceneName is None:
                    self.initializeFailed("SceneName is None")
                    pass

                if SceneManager.hasScene(self.SceneName) is False:
                    self.initializeFailed("Scene %s not found" % (self.SceneName))
                    pass
                pass
            pass
        pass

    def _onCheck(self):
        if self.SceneAny is False:
            if SceneManager.isSceneInit(self.SceneName) is True:
                return False
                pass
        else:
            if SceneManager.isChangeScene() is False:
                return False
                pass
            pass

        return True
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self._onSceneFilter)

        return False
        pass

    def _onSceneFilter(self, sceneName):
        if self.SceneAny is True:
            return True
            pass

        if self.SceneName != sceneName:
            return False
            pass

        return True
        pass
    pass