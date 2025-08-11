from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager

class CirclePairElementsManager(Manager):
    s_objects = {}

    class CirclePairElements(object):
        def __init__(self, movieNameList, movieActiveList, movieCloseList, movieSoundList, positionsList,
                     fieldMovieList):  # all args are list except first
            self.movieNameList = movieNameList
            self.movieActiveList = movieActiveList
            self.movieCloseList = movieCloseList
            self.positionsList = positionsList
            self.fieldMovieList = fieldMovieList
            self.movieSoundList = movieSoundList
            pass

        def getMovieNameList(self):
            return self.movieNameList

        def getMovieActiveList(self):
            return self.movieActiveList

        def getMovieCloseList(self):
            return self.movieCloseList

        def getPositionsList(self):
            return self.positionsList

        def getMovieSoundList(self):
            return self.movieSoundList

        def getFieldMovieList(self):
            return self.fieldMovieList

    @staticmethod
    def _onFinalize():
        CirclePairElementsManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            enigmaName = values.get("Name")

            collectionParam = values.get("Collection")
            fieldMovieList = values.get("FieldMovies")
            CirclePairElementsManager.loadCirclePairElementsCollection(module, enigmaName, collectionParam, fieldMovieList)
            pass

        return True

    @staticmethod
    def loadCirclePairElementsCollection(module, enigmaName, collectionParam, fieldMovieList):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        movieList = []
        movieActivateList = []
        movieCloseList = []
        movieSoundList = []
        positionList = []

        for values in records:
            MovieName = values.get("MovieName")
            movieList.append(MovieName)

            MovieActiveName = values.get("MovieActivate")
            movieActivateList.append(MovieActiveName)

            MovieCloseName = values.get("MovieClose")
            movieCloseList.append(MovieCloseName)

            MovieSoundName = values.get("MovieSound")
            movieSoundList.append(MovieSoundName)

            Positions = values.get("Positions")
            positionList.append(Positions)
            pass

        Object = CirclePairElementsManager.CirclePairElements(movieList, movieActivateList, movieCloseList,
                                                              movieSoundList, positionList, fieldMovieList)
        CirclePairElementsManager.s_objects[enigmaName] = Object
        pass

    @staticmethod
    def getCirclePairElements(name):
        if CirclePairElementsManager.hasCirclePairElements(name) is False:
            return None
            pass
        record = CirclePairElementsManager.s_objects[name]
        return record

    @staticmethod
    def hasCirclePairElements(name):
        if name not in CirclePairElementsManager.s_objects:
            Trace.log("CirclePairElementsManager", 0, "JoinBlocksManager.hasJoinBlocks: : not found %s" % (name))
            return False
        return True
