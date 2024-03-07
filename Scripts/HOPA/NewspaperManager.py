from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager


class NewspaperManager(Manager):
    s_newspapers = {}
    s_newspaperIds = {}
    s_newspapersOpens = []

    class Newspaper(object):
        def __init__(self, socket_Open, socket_Close, socket_BlockClose, movie_Open, movie_Close, attachGroupName, repeat):
            self.socket_Open = socket_Open
            self.socket_Close = socket_Close
            self.socket_BlockClose = socket_BlockClose
            self.movie_Open = movie_Open
            self.movie_Close = movie_Close
            self.attachGroupName = attachGroupName
            self.repeat = repeat

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            NewspaperID = record.get("NewspaperID")
            DemonName = record.get("DemonName")
            SocketOpen = record.get("SocketOpen")
            GroupName = record.get("GroupName")
            AttachGroupName = record.get("AttachGroupName")
            DefaultGroup = record.get("DefaultGroup")
            Repeat = bool(record.get("Repeat", 0))

            NewspaperManager.addNewspaper(NewspaperID, SocketOpen, DemonName, GroupName, AttachGroupName, DefaultGroup, Repeat)

        return True

    @classmethod
    def _onInitialize(cls, *args):
        cls.addObserver(Notificator.onSessionNew, NewspaperManager.__onSessionNew)

    @staticmethod
    def __onSessionNew(accountID):
        NewspaperManager.s_newspapersOpens = []
        return False

    @classmethod
    def _onSave(cls):
        return NewspaperManager.s_newspapersOpens
        pass

    @classmethod
    def _onLoad(cls, dict_save):
        NewspaperManager.s_newspapersOpens = dict_save
        pass

    @staticmethod
    def openNewspaper(newspaperID):
        if newspaperID in NewspaperManager.s_newspapersOpens:
            return
        NewspaperManager.s_newspapersOpens.append(newspaperID)

    @staticmethod
    def isOpenNewspaper(newspaperID):
        return newspaperID in NewspaperManager.s_newspapersOpens
        pass

    @staticmethod
    def addNewspaper(newspaperID, socketOpenName, demonName, groupName, attachGroupName, defaultGroupName, repeat):
        demon = GroupManager.getObject(groupName, demonName)

        Socket_Open = GroupManager.getObject(groupName, socketOpenName)
        Socket_Close = GroupManager.getObject(defaultGroupName, "Socket_Close")
        Socket_BlockClose = GroupManager.getObject(attachGroupName, "Socket_BlockClose")

        if demon.hasObject("Movie2_OpenNewspaper"):
            Movie_Open = demon.getObject("Movie2_OpenNewspaper")
            pass
        else:
            Movie_Open = GroupManager.getObject(defaultGroupName, "Movie2_OpenNewspaper")
            pass

        if demon.hasObject("Movie2_CloseNewspaper"):
            Movie_Close = demon.getObject("Movie2_CloseNewspaper")
            pass
        else:
            Movie_Close = GroupManager.getObject(defaultGroupName, "Movie2_CloseNewspaper")
            pass

        NewspaperManager.s_newspaperIds[(groupName, demonName)] = newspaperID

        NewspaperManager.s_newspapers[newspaperID] = NewspaperManager.Newspaper(Socket_Open, Socket_Close,
                                                                                Socket_BlockClose, Movie_Open,
                                                                                Movie_Close, attachGroupName, repeat)

    @staticmethod
    def hasNewspaperID(groupName, demonName):
        return (groupName, demonName) in NewspaperManager.s_newspaperIds
        pass

    @staticmethod
    def getNewspaperID(groupName, demonName):
        return NewspaperManager.s_newspaperIds[(groupName, demonName)]
        pass

    @staticmethod
    def hasNewspaper(name):
        return name in NewspaperManager.s_newspapers
        pass

    @staticmethod
    def getNewspaper(name):
        if name not in NewspaperManager.s_newspapers:
            Trace.log("Manager", 0, "NewspaperManager.getNewspaper: not found  %s" % (name))
            return None

        return NewspaperManager.s_newspapers[name]

    @staticmethod
    def getNewspapers():
        return NewspaperManager.s_newspapers

    @staticmethod
    def getNewspapersCount():
        return len(NewspaperManager.getNewspapers())
