from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class NotebookInventoryManager(object):
    s_showEntries = {}
    s_activateEntries = {}

    class ActivateEntry(object):
        def __init__(self, openTextID, closeTextID, openMovie, closeMovie):
            self.openTextID = openTextID
            self.closeTextID = closeTextID
            self.openMovie = openMovie
            self.closeMovie = closeMovie
            pass

        def getOpenTextID(self):
            return self.openTextID
            pass

        def getCloseTextID(self):
            return self.closeTextID
            pass

        def getOpenMovie(self):
            return self.openMovie
            pass

        def getCloseMovie(self):
            return self.closeMovie
            pass
        pass

    @staticmethod
    def onFinalize():
        NotebookInventoryManager.s_activateEntries = {}
        return False
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ActivateModuleName = record.get("ActivateModuleName")

            NotebookInventoryManager.addActivateEntries(module, ActivateModuleName)
            pass

        return True
        pass

    @staticmethod
    def addActivateEntries(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            NoteId = record.get("NoteId")
            ShowTextID = record.get("ShowTextID")
            CloseTextID = record.get("CloseTextID")
            ShowMovieGroup = record.get("ShowMovieGroup")
            ShowMovieName = record.get("ShowMovieName")
            CloseMovieGroup = record.get("CloseMovieGroup")
            CloseMovieName = record.get("CloseMovieName")

            OpenMovie = GroupManager.getObject(ShowMovieGroup, ShowMovieName)
            CloseMovie = GroupManager.getObject(CloseMovieGroup, CloseMovieName)

            NotebookInventoryManager.s_activateEntries[NoteId] = NotebookInventoryManager.ActivateEntry(ShowTextID, CloseTextID, OpenMovie, CloseMovie)
            pass

        pass

    @staticmethod
    def getActivateEntry(id):
        if NotebookInventoryManager.hasActivateEntry(id) is False:
            return None
            pass

        record = NotebookInventoryManager.s_activateEntries[id]
        return record
        pass

    @staticmethod
    def hasActivateEntry(id):
        if id not in NotebookInventoryManager.s_activateEntries:
            Trace.log("NotebookInventoryManager", 0, "NotebookInventoryManager.hasActivateEntry invalid data for entry %s, maybe forgot to add in some xls" % (id,))
            return False
            pass
        return True
        pass

    @staticmethod
    def getAllActivateEntries():
        return NotebookInventoryManager.s_activateEntries
        pass
    pass