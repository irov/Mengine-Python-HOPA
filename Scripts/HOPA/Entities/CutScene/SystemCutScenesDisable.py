from Foundation.System import System
from HOPA.CutSceneManager import CutSceneManager
from Notification import Notification

class SystemCutScenesDisable(System):
    def __init__(self):
        super(SystemCutScenesDisable, self).__init__()
        self.onLayerGroupPreparationObserver = None
        pass

    def _onRun(self):
        self.onLayerGroupPreparationObserver = Notification.addObserver(Notificator.onLayerGroupPreparation, self._onLayerGroupPreparation)
        return True
        pass

    def _onLayerGroupPreparation(self, groupName):
        if groupName == "CutScene":
            self._disableContent()
            return False
            pass
        return False
        pass

    def _disableContent(self):
        allMovies = CutSceneManager.getAllMovies()
        for movie in allMovies:
            if movie.getName() == "Movie_CutScene":
                continue
                pass
            movie.setEnable(False)
            pass
        pass

    def _onStop(self):
        Notification.removeObserver(self.onLayerGroupPreparationObserver)
        self.onLayerGroupPreparationObserver = None
        pass

    pass