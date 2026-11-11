from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.HintAction import HintAction


class HintActionHOG(MixinGroup, HintAction):
    def _onAction(self, source, hint):
        # dummy: ends at once (was the old cb(False) API)
        self.setEnd()
        pass

    def _onCheck(self):
        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName == self.SceneName:
            return False
            pass

        return True
        pass

    pass
