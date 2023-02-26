from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.HintAction import HintAction

class HintActionHOG(MixinGroup, HintAction):
    def _onAction(self, hint, cb):
        cb(False)
        # dummy
        pass

    def _onCheck(self):
        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName == self.SceneName:
            return False
            pass

        return True
        pass

    pass