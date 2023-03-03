from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class NotebookManager(object):
    s_entries = {}
    s_notes = {}

    class NotebookEntry(object):
        def __init__(self, openMovie, closeMovie, selectOpenMovie, selectCloseMovie):
            self.openMovie = openMovie
            self.closeMovie = closeMovie
            self.selectOpenMovie = selectOpenMovie
            self.selectCloseMovie = selectCloseMovie
            pass

        def getOpenMovie(self):
            return self.openMovie
            pass

        def getCloseMovie(self):
            return self.closeMovie
            pass

        def getSelectOpenMovie(self):
            return self.selectOpenMovie
            pass

        def getSelectCloseMovie(self):
            return self.selectCloseMovie
            pass

        pass

    @staticmethod
    def onFinalize():
        NotebookManager.s_desciptionList = ()
        NotebookManager.s_notes = {}
        return False
        pass

    @staticmethod
    def loadNotebook(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            IDNotes = record.get("IDNotes")
            ModuleTextName = record.get("ModuleTextName")
            ModuleName = record.get("ModuleName")

            NotebookManager.addNotebookEntries(module, ModuleName)
            NotebookManager.addTextes(module, ModuleTextName)
            pass

        pass

    @staticmethod
    def addTextes(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            NoteID = record.get("NoteID")
            ListedTextID = record.get("NoteTextID")

            NotebookManager.s_notes[NoteID] = ListedTextID
            pass
        pass

    @staticmethod
    def addNotebookEntries(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Position = record.get("Position")
            GroupName = record.get("NoteGroup")
            OpenMovieName = record.get("OpenMovieName")
            CloseMovieName = record.get("CloseMovieName")
            SelectOpenMovieName = record.get("SelectOpenMovieName")
            SelectCloseMovieName = record.get("SelectCloseMovieName")

            OpenMovie = GroupManager.getObject(GroupName, OpenMovieName)
            CloseMovie = GroupManager.getObject(GroupName, CloseMovieName)
            SelectOpenMovie = GroupManager.getObject(GroupName, SelectOpenMovieName)
            SelectCloseMovie = GroupManager.getObject(GroupName, SelectCloseMovieName)

            NotebookManager.s_entries[Position] = NotebookManager.NotebookEntry(OpenMovie, CloseMovie, SelectOpenMovie, SelectCloseMovie)
            pass

        pass

    @staticmethod
    def getNote(id):
        if NotebookManager.hasNote(id) is False:
            return None
            pass

        record = NotebookManager.s_notes[id]
        return record
        pass

    @staticmethod
    def hasNote(id):
        if id not in NotebookManager.s_notes:
            Trace.log("NotebookManager", 0, "NotebookManager.hasNote invalid ID, maybe forgot to add in some xls")
            return False
            pass

        return True
        pass

    @staticmethod
    def getEntry(pos):
        if NotebookManager.hasEntry(pos) is False:
            return None
            pass

        record = NotebookManager.s_entries[pos]
        return record
        pass

    @staticmethod
    def hasEntry(pos):
        if pos not in NotebookManager.s_entries:
            Trace.log("NotebookManager", 0, "NotebookManager.hasEntry invalid position for entry, maybe forgot to add in some xls")
            return False
            pass

        return True

        pass

    @staticmethod
    def getAllEntries():
        return NotebookManager.s_entries
        pass

    pass
