from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.CruiseAction import CruiseAction


class CruiseActionHOG(MixinGroup, CruiseAction):
    def _onAction(self, hint, cb):
        cb(False)
        # dummy
        pass

    def _onCheck(self):
        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName == self.SceneName:
            return False

        return True
