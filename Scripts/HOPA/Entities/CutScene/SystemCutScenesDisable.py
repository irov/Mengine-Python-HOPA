from Foundation.System import System
from HOPA.CutSceneManager import CutSceneManager


class SystemCutScenesDisable(System):

    def _onRun(self):
        self.addObserver(Notificator.onLayerGroupPreparation, self._onLayerGroupPreparation)
        return True

    def _onLayerGroupPreparation(self, groupName):
        if groupName == "CutScene":
            self._disableContent()
            return False
        return False

    def _disableContent(self):
        allMovies = CutSceneManager.getAllMovies()
        for movie in allMovies:
            if movie.getName() == "Movie_CutScene":
                continue
            movie.setEnable(False)
