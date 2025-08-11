from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager


class JournalManager(Manager):
    s_pages = {}
    s_sequencePagesID = {}
    s_journalIDs_order = []

    class Page(object):
        def __init__(self, groupName, nextPageID, textIDs, cutScene):
            self.groupName = groupName
            self.nextPageID = nextPageID
            self.textIDs = textIDs
            self.cutScene = cutScene

    @staticmethod
    def _onFinalize():
        JournalManager.s_pages = {}
        JournalManager.s_sequencePagesID = {}
        JournalManager.s_journalIDs_order = []
        pass

    @staticmethod
    def setSequencePagesID(dict):
        JournalManager.s_sequencePagesID = dict
        pass

    @staticmethod
    def getSequencePagesID():
        return JournalManager.s_sequencePagesID

    @staticmethod
    def cleanSequencePagesID():
        JournalManager.s_sequencePagesID = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            JournalID = record.get("JournalID")

            if JournalID is None:
                continue
                pass

            GroupName = record.get("GroupName")
            NextPageID = record.get("NextPageID")

            CutScene = record.get("CutSceneName", None)
            TextIDs = record.get("TextIDs")

            cs_TextIDS = []
            if TextIDs is not None:
                for TextID in TextIDs:
                    cs_TextIDS.append(TextID)
                    pass
                pass

            DynamicJournal = DefaultManager.getDefaultBool("DynamicJournal", True)
            if DynamicJournal is True:
                JournalManager.s_sequencePagesID[JournalID] = NextPageID
                pass

            JournalManager.addJournalPage(JournalID, GroupName, NextPageID, cs_TextIDS, CutScene)
            pass

        return True
        pass

    @staticmethod
    def loadJournalBlocks(param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            JournalIDs = record.get("JournalID")
            JournalManager.s_blocks.append(JournalIDs)
            pass
        pass

    @staticmethod
    def addJournalPage(JournalID, groupName, nextPageID, textIDs, cutScene):
        if JournalID in JournalManager.s_pages:
            Trace.log("Manager", 0, "JournalManager addJournalPage: page %s already exist" % (JournalID))
            return
            pass

        Page = JournalManager.Page(groupName, nextPageID, textIDs, cutScene)

        JournalManager.s_pages[JournalID] = Page
        JournalManager.s_journalIDs_order.append(JournalID)  # for debug

    @staticmethod
    def getJournalPage(JournalID):
        if JournalID not in JournalManager.s_pages:
            Trace.log("Manager", 0, "JournalManager.getJournalPage: Error!!!!!!!!!!!!!!!!! %s not add in JournalPages!!!!" % JournalID)
            return None
            pass

        return JournalManager.s_pages[JournalID]
        pass

    @staticmethod
    def addPageNext(currentPage, nextPageID):
        JournalManager.s_sequencePagesID[currentPage] = nextPageID
        pass

    @staticmethod
    def getPreviousPage(JournalID):
        Journal = DemonManager.getDemon("Journal")
        PageID = Journal.getParam("PageID")

        for id in JournalManager.s_sequencePagesID.keys():
            if JournalManager.s_sequencePagesID[id] == JournalID:
                if id not in PageID:
                    return None
                return id
        return None

    @staticmethod
    def getNextPage(JournalID):
        Journal = DemonManager.getDemon("Journal")

        PageID = Journal.getParam("PageID")
        if JournalID not in JournalManager.s_sequencePagesID:
            return None

        next = JournalManager.s_sequencePagesID[JournalID]
        if next not in PageID:
            return None

        return next

    @staticmethod
    def getAllPages():
        return JournalManager.s_pages

    @staticmethod
    def getOrderedAllJournalIDs():
        return JournalManager.s_journalIDs_order
