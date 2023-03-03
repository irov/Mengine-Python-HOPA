from Foundation.DatabaseManager import DatabaseManager


class MenuHelpManager(object):
    s_pages = {}
    s_sequencePagesID = {}

    class Page(object):
        def __init__(self, groupName, nextPageID, textIDs):
            self.groupName = groupName
            self.nextPageID = nextPageID
            self.textIDs = textIDs

    @staticmethod
    def onFinalize():
        MenuHelpManager.s_pages = {}
        MenuHelpManager.s_sequencePagesID = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            PageID = record.get("PageID")
            NextPageID = record.get("NextPageID")
            GroupName = record.get("GroupName")
            TextIDs = record.get("TextIDs")

            cs_TextIDs = []
            for TextID in TextIDs:
                cs_TextIDs.append(TextID)

            Page = MenuHelpManager.Page(GroupName, NextPageID, cs_TextIDs)

            MenuHelpManager.s_pages[PageID] = Page
            MenuHelpManager.s_sequencePagesID[PageID] = NextPageID
            pass

        return True

    @staticmethod
    def getPreviousPage(id):
        for tempId, nextId in MenuHelpManager.s_sequencePagesID.iteritems():
            if nextId == id:
                return tempId

        return None
        pass

    @staticmethod
    def getPage(id):
        if id not in MenuHelpManager.s_pages.keys():
            return None

        return MenuHelpManager.s_pages[id]

    @staticmethod
    def getNextPage(id):
        if id not in MenuHelpManager.s_sequencePagesID.values():
            return None

        return MenuHelpManager.s_sequencePagesID[id]
