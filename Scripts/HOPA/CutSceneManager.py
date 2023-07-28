from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from HOPA.ScenarioManager import ScenarioManager


class CutSceneManager(object):
    manager_dict = {}
    allMovies = []

    class SingleCutScene(object):
        def __init__(self, CutSceneID, MovieGroupName, MovieName, MovieText, NextID):
            self.CutSceneID = CutSceneID
            self.MovieName = MovieName
            self.MovieGroupName = MovieGroupName
            self.MovieText = MovieText
            self.NextSceneID = NextID
            pass

        def getMovie(self):
            if self.MovieName is None or self.MovieGroupName is None:
                return None
                pass

            Movie_Object = GroupManager.getObject(self.MovieGroupName, self.MovieName)

            return Movie_Object
            pass

        def getMovieText(self):
            if self.MovieText is None or self.MovieGroupName is None:
                return None
                pass

            Movie_Object = GroupManager.getObject(self.MovieGroupName, self.MovieText)

            return Movie_Object
            pass

        def getGroup(self):
            if self.MovieName is None or self.MovieGroupName is None:
                return None
                pass
            return self.MovieGroupName

        def getNext(self):
            return self.NextSceneID

    @staticmethod
    def onFinalize():
        CutSceneManager.manager_dict = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            MovieName = record.get("MovieName")
            MovieGroupName = record.get("MovieGroupName")
            CutSceneID = record.get("CutSceneID")
            MovieText = record.get("MovieText")
            NextID = record.get("NextSceneID")

            if isinstance(GroupManager.getGroup(MovieGroupName), GroupManager.EmptyGroup):
                continue

            MovieObject = GroupManager.getObject(MovieGroupName, MovieName)

            if MovieObject is None:
                Trace.log("Manager", 0,
                          "CutSceneManager.loadParams: not found movie object [%s:%s]" % (MovieGroupName, MovieName))
                return False
                pass

            CutSceneManager.allMovies.append(MovieObject)

            CutSceneManager.addRow(CutSceneID, MovieGroupName, MovieName, MovieText, NextID)
            pass

        return True
        pass

    @staticmethod
    def getAllMovies():
        return CutSceneManager.allMovies
        pass

    @staticmethod
    def addRow(CutSceneID, MovieGroupName, MovieName, MovieText, NextID):
        if not CutSceneID or not MovieGroupName or not MovieName:
            Trace.log("Manager", 0, "CutSceneManager addRow: input key data error")
            pass

        data = CutSceneManager.SingleCutScene(CutSceneID, MovieGroupName, MovieName, MovieText, NextID)
        key = CutSceneID
        # subkey = MovieGroupName   # {ItemName:{SocketName:classObj,SocketAnotherName:classObj}}
        # sub_dict = {}
        # sub_dict[subkey] = data
        CutSceneManager.manager_dict[key] = data
        pass

    @staticmethod
    def hasScene(SceneID):
        return SceneID in CutSceneManager.manager_dict
        pass

    @staticmethod
    def hasMovie(ID, MovieName):
        if CutSceneManager.hasScene(ID) is True:
            return CutSceneManager.manager_dict[ID] == MovieName
        return False

    @staticmethod
    def getItem(SceneID):
        item = CutSceneManager.manager_dict.get(SceneID)

        if item is None or isinstance(item.MovieGroupName, GroupManager.EmptyGroup):
            return None

        if CutSceneManager.hasScene(SceneID) is False:
            Trace.log("Manager", 0, "CutSceneManager.getItem: not found cut scene %s " % (SceneID))
            return None

        return item

    @staticmethod
    def getMovie(SceneId):
        record = CutSceneManager.getItem(SceneId)

        if record is None:
            return
            pass

        return record.getMovie()
        pass

    @staticmethod
    def getMovieText(SceneId):
        record = CutSceneManager.getItem(SceneId)

        if record is None:
            return
            pass

        return record.getMovieText()
        pass

    @staticmethod
    def getGroup(SceneId):
        record = CutSceneManager.getItem(SceneId)
        if record is None:
            return

        return record.getGroup()
        pass

    @staticmethod
    def getNext(SceneId):
        record = CutSceneManager.getItem(SceneId)
        if record is None:
            return
        return record.getNext()
        pass

    @staticmethod
    def disableAll():
        for cutData in CutSceneManager.manager_dict.values():
            movie = cutData.getMovie()
            movie.setEnable(False)

    @staticmethod
    def findPreviousCutSceneParagraph(cutscene_name):
        if cutscene_name is None:
            Trace.log("Manager", 4, "findPreviousCutSceneParagraph failed: cutscene_name is None")
            return None

        scenarios = ScenarioManager.getSceneRunScenarios("CutScene", "CutScene")

        if len(scenarios) == 0:
            Trace.log("Manager", 4, "findPreviousCutSceneParagraph [{}]: no scenarios found".format(cutscene_name))
            return None

        paragraph_id = None
        for runner in scenarios:
            scenario = runner.getScenario()
            for paragraph in scenario.getParagraphs():
                for macro in paragraph.getAllCommands():
                    if macro.CommandType != "PlayCutScene":
                        continue
                    for value in macro.Values:
                        if value == cutscene_name:
                            paragraph_id = paragraph.Paragraphs[0]
                            break

        if paragraph_id is None:
            Trace.log("Manager", 4, "findPreviousCutSceneParagraph [{}]: not found any paragraph".format(cutscene_name))
            return None

        return paragraph_id
