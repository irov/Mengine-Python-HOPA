import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class TipManager(object):
    s_tips = {}
    s_movieTips = {}

    class Tip(object):
        def __init__(self, object, notifies, textId, tipID):
            self.object = object
            self.notifies = notifies

            self.textId = textId
            self.tipID = tipID
            pass
        pass

    @staticmethod
    def loadMovieTips(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            TipId = record.get("TipId")
            GroupName = record.get("GroupName")
            MovieName = record.get("MovieName")

            movie = GroupManager.getObject(GroupName, MovieName)

            TipManager.s_movieTips[TipId] = movie
            pass
        pass

    @staticmethod
    def isMovieTip(tipId):
        return tipId in TipManager.s_movieTips
        pass

    @staticmethod
    def getMovieTip(tipId):
        if TipManager.isMovieTip(tipId) is False:
            Trace.log("TipManager", 0, "TipManager.getMovieTip  tip with id -->%s<-- is not MovieTip" % (tipId,))
            return None
            pass
        movie = TipManager.s_movieTips[tipId]
        return movie
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            TipId = record.get("TipId")
            TextId = record.get("TextId")

            TipManager.addTipID(TipId, TextId)
            pass

        return True
        pass

    @staticmethod
    def hasTip(tipId):
        return tipId in TipManager.s_tips
        pass

    @staticmethod
    def getTextID(tipId):
        return TipManager.s_tips[tipId]
        pass

    @staticmethod
    def createTip(object, notifies, tipID):
        if TipManager.hasTip(tipID) is False:
            Trace.log("TipManager", 0, "createTip.addTipObjectParams: TipID is not initialize!")
            return None
            pass

        textId = TipManager.getTextID(tipID)
        Tip = TipManager.Tip(object, notifies, textId, tipID)

        return Tip
        pass

    @staticmethod
    def addTipID(tipId, textId):
        TipManager.s_tips[tipId] = textId
        pass
    pass