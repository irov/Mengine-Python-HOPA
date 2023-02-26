from Foundation.DatabaseManager import DatabaseManager

class StaticPopUpTransitionManager(object):
    """
    Mark transition back with text and movie
    """
    s_objects = {}

    class SceneTransitionUp(object):
        def __init__(self, sceneName, textId, movieName, offset):
            self.textId = textId
            self.sceneName = sceneName
            self.movieName = movieName
            self.offset = offset
            pass
        pass

        def getTextId(self):
            return self.textId
            pass

    @staticmethod
    def onFinalize():
        StaticPopUpTransitionManager.s_objects = {}
        pass

    @staticmethod
    def load(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            SceneName = record.get("SceneName")
            TextId = record.get("TextId")
            MovieName = record.get("MovieName")
            Offset = record.get("Offset")
            dataObject = StaticPopUpTransitionManager.SceneTransitionUp(SceneName, TextId, MovieName, Offset)
            StaticPopUpTransitionManager.s_objects[SceneName] = dataObject
            pass
        pass

    @staticmethod
    def getPopUp(sceneName):
        dataObject = StaticPopUpTransitionManager.s_objects.get(sceneName)
        if dataObject is None:
            Trace.log("Manager", 0, "StaticPopUpTransitionManager: SceneName doest exist %s" % (sceneName,))
            return
        else:
            return dataObject
            pass
        pass

    @staticmethod
    def getTextId(sceneName):
        data = StaticPopUpTransitionManager.getPopUp(sceneName)
        if data is None:
            return
            pass

        textId = data.getTextId()
        return textId
        pass

    @staticmethod
    def getMovieName(sceneName):
        data = StaticPopUpTransitionManager.getPopUp(sceneName)
        movieName = data.movieName
        return movieName
        pass

    @staticmethod
    def getOffset(sceneName):
        data = StaticPopUpTransitionManager.getPopUp(sceneName)
        offset = data.offset
        return offset
        pass