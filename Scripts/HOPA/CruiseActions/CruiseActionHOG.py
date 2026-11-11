from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.CruiseAction import CruiseAction


class CruiseActionHOG(MixinGroup, CruiseAction):
    def _onAction(self, source):
        # dummy: SystemCruiseControl listens for the end only after onAction returns, so end on the next frame
        source.addDelay(0.0)  # delay one frame
        source.addNotify(Notificator.onCruiseActionEnd, self)

    def _onCheck(self):
        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName == self.SceneName:
            return False

        return True
