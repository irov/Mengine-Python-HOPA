from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionTransitionBackMobile(HintActionDefault):

    def _getHintObject(self):
        SystemNavigation = SystemManager.getSystem("SystemNavigation")
        button = SystemNavigation.getNavGoBackButton()

        return button

    def _getHintPosition(self, Object):
        SystemNavigation = SystemManager.getSystem("SystemNavigation")
        button = SystemNavigation.getNavGoBackButton()

        if button is not None:
            Position = button.getCurrentMovieSocketCenter()
            return Position

        return 0.0, 0.0, 0.0

    def _onCheck(self):
        return EnigmaManager.getSceneActiveEnigma() is None

    def getHintLayer(self):
        scene = SceneManager.getCurrentScene()
        layer = scene.getSlot("HintEffect")
        return layer
