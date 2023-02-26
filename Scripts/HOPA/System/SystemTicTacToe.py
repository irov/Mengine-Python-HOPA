from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.TransitionManager import TransitionManager

class SystemTicTacToe(System):
    def _onParams(self, params):
        super(SystemTicTacToe, self)._onParams(params)

    def _onRun(self):
        self.addObserver(Notificator.onTicTacToePlayerChange, self.__printCurrentPlayer)
        self.addObserver(Notificator.onTicTacToeSceneTransition, self.__transitionTo)

        return True

    def _onStop(self):
        pass

    def __printCurrentPlayer(self, current_player):
        return False

    def __transitionTo(self, scene_name):
        if scene_name is None:
            return False

        current_scene_name = SceneManager.getCurrentSceneName()
        if DemonManager.hasDemon(scene_name):
            demon = DemonManager.getDemon(scene_name)
            demon.setParam("PreviousSceneName", current_scene_name)

        TransitionManager.changeScene(scene_name)
        return False