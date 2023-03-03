from Foundation.DemonManager import DemonManager
from Foundation.System import System


class SystemMapSave(System):
    def __init__(self):
        super(SystemMapSave, self).__init__()

        self.Map = DemonManager.getDemon("Map")
        pass

    def _onSave(self):
        VisitScenes = self.Map.getParam("VisitScenes")
        MarkedDone = self.Map.getParam("MarkedDone")
        CurrentID = self.Map.getParam("CurrentID")
        OpenPages = self.Map.getParam("OpenPages")

        return (VisitScenes, MarkedDone, CurrentID, OpenPages)
        pass

    def _onLoad(self, data_save):
        VisitScenes, MarkedDone, CurrentID, OpenPages = data_save

        self.Map.setParam("VisitScenes", VisitScenes)
        self.Map.setParam("MarkedDone", MarkedDone)
        self.Map.setParam("CurrentID", CurrentID)
        self.Map.setParam("OpenPages", OpenPages)
        pass

    def _onRun(self):
        return True
        pass

    def _onStop(self):
        self.Map.removeAllData()
        self.Map = None
        pass

    pass
