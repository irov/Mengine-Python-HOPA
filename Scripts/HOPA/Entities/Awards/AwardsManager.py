from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class AwardsManager(object):
    s_awards = {}
    s_awardsData = {}
    s_noSkipPuzzle = {}
    s_noHintHog = {}
    s_hogItemTime = {}
    s_enigmaTime = {}
    s_bonusItems = {}
    s_hogClickCounts = {}
    s_enigmaNoResets = {}
    s_resetGroups = []
    s_openMovies = {}
    s_tasksComplete = {}
    s_diffAward = {}
    ENIGMA_TIME = 60

    class AwardData(object):
        def __init__(self, Count, MovieName, OpenTextID, ImageCount):
            self.count = Count
            self.movieName = MovieName
            self.OpenTextID = OpenTextID
            self.ImageCount = ImageCount
            pass

        def getCount(self):
            return self.count
            pass

        def getMovieName(self):
            return self.movieName
            pass

        def getOpenTextID(self):
            return self.OpenTextID
            pass

        def getImageCount(self):
            return self.ImageCount
            pass

        pass

    pass

    @staticmethod
    def onFinalize():
        AwardsManager.s_awards = {}
        AwardsManager.s_awardsData = {}
        AwardsManager.s_noSkipPuzzle = {}
        AwardsManager.s_noHintHog = {}
        AwardsManager.s_hogItemTime = {}
        AwardsManager.s_enigmaTime = {}
        AwardsManager.s_bonusItems = {}
        AwardsManager.s_hogClickCounts = {}
        AwardsManager.s_enigmaNoResets = {}
        AwardsManager.s_tasksComplete = {}
        AwardsManager.s_openMovies = {}
        AwardsManager.s_diffAward = {}
        AwardsManager.s_resetGroups = {}  # PuzzleButtons groupnames with reset button inside demon
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Awards":
            AwardsManager.loadAwards(module, param)
            pass
        if param == "AwardsPuzzleNoSkip":
            AwardsManager.loadPuzzleNoSkip(module, param)
            pass
        if param == "AwardsHOGNoHint":
            AwardsManager.loadHogNoHint(module, param)
            pass
        if param == "AwardsHOGItemTime":
            AwardsManager.loadHogItemTime(module, param)
            pass
        if param == "AwardsEnigmaTime":
            AwardsManager.loadEnigmaTime(module, param)
            pass
        if param == "AwardsBonusItems":
            AwardsManager.loadBonusItems(module, param)
            pass
        if param == "AwardsDifficult":
            AwardsManager.loadAwardsDifficult(module, param)
            pass
        pass

    @staticmethod
    def loadAwards(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")
            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")

            MovieName = record.get("MovieName")
            OpenTextID = record.get("OpenTextID")
            ImageCount = bool(record.get("ImageCount", 1))

            AwardsManager.addAward(AwardID, GroupName, ObjectName, Count, MovieName, OpenTextID, ImageCount)
            pass
        pass

    @staticmethod
    def addAward(AwardID, GroupName, ObjectName, Count, MovieName, OpenTextID, ImageCount):
        Award = GroupManager.getObject(GroupName, ObjectName)
        AwardData = AwardsManager.AwardData(Count, MovieName, OpenTextID, ImageCount)
        AwardsManager.s_awardsData[Award] = AwardData
        AwardsManager.s_awards[AwardID] = Award
        pass

    @staticmethod
    def getAwardData(object):
        if object not in AwardsManager.s_awardsData:
            Trace.log("Manager", 0, "AwardsManager: getAwardData not found object[%s], not add in Award in properly Group" % object)
            return None
            pass

        return AwardsManager.s_awardsData[object]
        pass

    @staticmethod
    def getAwards(id):
        if id not in AwardsManager.s_awards:
            Trace.log("Manager", 0, "AwardsManager: getAwards not found id[%s], not add in Awards.xlsx" % id)
            return None
            pass

        return AwardsManager.s_awards[id]
        pass

    pass

    @staticmethod
    def loadAwardsDifficult(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            AwardID = record.get("AwardID")
            Difficulty = record.get("Difficulty")

            AwardsManager.s_diffAward[unicode(Difficulty)] = AwardID
        pass

    @staticmethod
    def getDiffAward(diff):
        if diff not in AwardsManager.s_diffAward:
            return None
            pass
        return AwardsManager.s_diffAward[diff]
        pass

    @staticmethod
    def loadHogNoHint(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")

            AwardsManager.s_noHintHog[Count] = AwardID
            pass
        pass

    @staticmethod
    def loadTasksComplete(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            NoteID = record.get("NoteID")

            AwardsManager.s_tasksComplete[NoteID] = AwardID
            pass
        pass

    @staticmethod
    def loadPuzzleNoSkip(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")

            AwardsManager.s_noSkipPuzzle[Count] = AwardID
            pass
        pass

    @staticmethod
    def loadBonusItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Param = record.get("Param")
            AwardsManager.addBonusItem(AwardID, module, Param)
            pass
        pass

    @staticmethod
    def addBonusItem(AwardID, module, param):
        listObjects = []
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")
            Object = GroupManager.getObject(GroupName, ObjectName)
            listObjects.append(Object)
            pass

        AwardsManager.s_bonusItems[AwardID] = listObjects
        pass

    @staticmethod
    def loadHogItemTime(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")

            AwardsManager.s_hogItemTime[Count] = AwardID
            pass
        pass

    @staticmethod
    def loadEnigmaTime(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")
            Time = record.get("Time")
            if Time is not None:
                AwardsManager.ENIGMA_TIME = Time
                pass

            AwardsManager.s_enigmaTime[Count] = AwardID
            pass
        pass

    @staticmethod
    def getEnigmaTimeLimit():  # worth it
        return AwardsManager.ENIGMA_TIME
        pass

    @staticmethod
    def getBonusItems():
        return AwardsManager.s_bonusItems
        pass

    @staticmethod
    def getEnigmaTimeAwardID(count):
        if count not in AwardsManager.s_enigmaTime:
            return None

        return AwardsManager.s_enigmaTime[count]
        pass

    @staticmethod
    def getNoSkipAwardID(count):
        if count not in AwardsManager.s_noSkipPuzzle:
            return None

        return AwardsManager.s_noSkipPuzzle[count]
        pass

    @staticmethod
    def getNoHintAwardID(count):
        if count not in AwardsManager.s_noHintHog:
            return None

        return AwardsManager.s_noHintHog[count]
        pass

    @staticmethod
    def getHogItemTimeAwardID(count):
        if count not in AwardsManager.s_hogItemTime:
            return None

        return AwardsManager.s_hogItemTime[count]
        pass

    @staticmethod
    def getTasksCompleteAwardID(id):
        if id not in AwardsManager.s_tasksComplete:
            return None
            pass

        return AwardsManager.s_tasksComplete[id]
        pass

    # ------------------------------------------

    @staticmethod
    def loadHogClickCount(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")
            OverHead = record.get("OverClicks")
            AwardsManager.s_hogClickCounts[Count] = (AwardID, OverHead)
            pass
        pass

    @staticmethod
    def getAwardWithClickCount(Count):
        awardTuple = AwardsManager.s_hogClickCounts.get(Count)
        return awardTuple
        pass

    @staticmethod
    def loadEnigmaNoReset(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            Count = record.get("Count")
            GroupsList = record.get("ResetGroups")
            if GroupsList is not None:
                AwardsManager.s_resetGroups = GroupsList
            AwardsManager.s_enigmaNoResets[Count] = AwardID
            pass
        pass

    @staticmethod
    def getAwardWithResetCount(Count):
        award = AwardsManager.s_enigmaNoResets.get(Count)
        return award
        pass

    @staticmethod
    def getAwardResetGroups():
        groups = AwardsManager.s_resetGroups
        return groups
        pass

    @staticmethod
    def loadAwardsOpenMovies(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            AwardID = record.get("AwardID")
            MovieName = record.get("Movie")
            GroupName = record.get("Group")
            if GroupManager.hasObject(GroupName, MovieName) is False:
                Trace.log("Manager", 0, "AwardsManager.loadAwardsOpenMovies cant find movie: %s on group: %s" % (MovieName, GroupName))
                continue
            Movie = GroupManager.getObject(GroupName, MovieName)
            AwardsManager.s_openMovies[AwardID] = Movie
            pass
        pass

    @staticmethod
    def getAwardOpenMovie(awardId):
        movie = AwardsManager.s_openMovies.get(awardId)
        return movie
        pass

    pass

pass