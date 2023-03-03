from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class Journal2Manager(object):
    s_pages = {}

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            JournalID = record.get("JournalID")
            GroupName = record.get("GroupName")
            MovieName = record.get("MovieName")

            movie = GroupManager.getObject(GroupName, MovieName)
            Journal2Manager.s_pages[JournalID] = movie
            pass
        pass

    @staticmethod
    def hasPage(pageID):
        if pageID not in Journal2Manager.s_pages:
            return False
            pass
        return True
        pass

    @staticmethod
    def getPage(pageID):
        if Journal2Manager.hasPage(pageID) is False:
            Trace.log("Manager", 0, "Journal2Manager.getPage not found page %s" % (pageID))
            return None
            pass
        page = Journal2Manager.s_pages[pageID]
        return page
        pass

    @staticmethod
    def getAllPages():
        return Journal2Manager.s_pages
        pass

    pass
