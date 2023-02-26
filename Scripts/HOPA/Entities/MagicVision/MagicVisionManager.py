import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class MagicVisionManager(object):
    s_movies = {}
    s_scenes = {}
    s_backScenes = {}
    s_backMovies = {}
    @staticmethod
    def onFinalize():
        MagicVisionManager.s_movies = {}
        MagicVisionManager.s_scenes = {}
        MagicVisionManager.s_backScenes = {}
        pass

    @staticmethod
    def loadMagicVision(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            SceneName = values.get("SceneName")
            GroupName = values.get("GroupName")
            ActivateMovieName = values.get("ActivateMovieName")
            SceneNameTo = values.get("SceneNameTo")
            GroupNameTo = values.get("GroupNameTo")
            DeactivateMovieName = values.get("DeactivateMovieName")

            movieActivate = None
            movieDeactivate = None

            if GroupManager.hasObject(GroupName, ActivateMovieName) is True:
                movieActivate = GroupManager.getObject(GroupName, ActivateMovieName)
                pass
            else:
                Trace.log("MagicVisionManager", 0, "MagicVisionManager.loadMagicVision :: invalid parameters for Activate movies on Group:%s Scene:%s" % (GroupName, SceneName))
                pass

            if GroupManager.hasObject(GroupNameTo, DeactivateMovieName) is True:
                movieDeactivate = GroupManager.getObject(GroupNameTo, DeactivateMovieName)
                pass
            else:
                Trace.log("MagicVisionManager", 0, "MagicVisionManager.loadMagicVision :: invalid parameters for Deactivate movies on Group:%s Scene:%s" % (GroupNameTo, SceneNameTo))
                pass

            MagicVisionManager.s_scenes[SceneName] = SceneNameTo
            MagicVisionManager.s_movies[SceneName] = movieActivate
            MagicVisionManager.s_backScenes[SceneNameTo] = SceneName
            MagicVisionManager.s_backMovies[SceneNameTo] = movieDeactivate
            pass
        pass

    @staticmethod
    def getSceneNameTo(sceneNameFrom):
        if sceneNameFrom not in MagicVisionManager.s_scenes:
            return None
            pass
        return MagicVisionManager.s_scenes[sceneNameFrom]
        pass

    @staticmethod
    def getSceneNameFrom(sceneNameTo):
        if sceneNameTo not in MagicVisionManager.s_backScenes:
            return None
            pass
        return MagicVisionManager.s_backScenes[sceneNameTo]
        pass

    @staticmethod
    def getActivateMovie(sceneNameFrom):
        if sceneNameFrom not in MagicVisionManager.s_movies:
            return None
            pass
        return MagicVisionManager.s_movies[sceneNameFrom]
        pass

    @staticmethod
    def getDeactivateMovie(sceneNameFrom):
        if sceneNameFrom not in MagicVisionManager.s_backMovies:
            return None
            pass
        return MagicVisionManager.s_backMovies[sceneNameFrom]
        pass

    @staticmethod
    def hasActivateMovie(sceneName):
        if sceneName in MagicVisionManager.s_movies:
            return True
            pass
        return False
        pass

    @staticmethod
    def hasDeactivateMovie(sceneName):
        if sceneName in MagicVisionManager.s_backMovies:
            return True
            pass
        return False
        pass

    @staticmethod
    def isMagicVisionScene(sceneName):
        if sceneName not in MagicVisionManager.s_backScenes:
            return False
            pass
        return True
        pass

    pass