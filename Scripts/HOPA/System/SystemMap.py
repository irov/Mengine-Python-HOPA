from Foundation.DemonManager import DemonManager
from Foundation.System import System


class SystemMap(System):
    def _onParams(self, params):
        super(SystemMap, self)._onParams(params)
        self.Teleport = params.get("Teleport", True)
        self.Map = DemonManager.getDemon("Map")
        pass

    def _onRun(self):
        self.Map.setParam("Teleport", self.Teleport)

        self.addObserver(Notificator.onSceneEnter, self._appendVisitScenes)
        self.addObserver(Notificator.onMapMarked, self._markDone)

        return True
        pass

    def _appendVisitScenes(self, sceneName):
        VisitScenes = self.Map.getParam("VisitScenes")
        if sceneName in VisitScenes:
            return False
            pass

        self.Map.appendParam("VisitScenes", sceneName)
        return False
        pass

    def _markDone(self, sceneName):
        self.Map.appendParam("MarkedDone", sceneName)
        return False
        pass

    def _onStop(self):
        pass

    pass
