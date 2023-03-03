from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class NotebookDescriptionManager(object):
    s_descriptions = {}

    class DescriptionEntry(object):
        def __init__(self, textID, Movie):
            self.textID = textID
            self.Movie = Movie

        def getTextID(self):
            return self.textID
            pass

        def getMovie(self):
            return self.Movie
            pass

        pass

    @staticmethod
    def onFinalize():
        NotebookDescriptionManager.s_descriptions = ()
        return False
        pass

    @staticmethod
    def loadNotebookDescription(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ModuleName = record.get("DescriptionModuleName")

            NotebookDescriptionManager.addDescriptionsEntries(module, ModuleName)
            pass
        pass

    @staticmethod
    def addDescriptionsEntries(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            NoteID = record.get("NoteID")
            DescriptionTextID = record.get("DescriptionTextID")
            DescriptionGroupName = record.get("DescriptionGroupName")
            DescriptionMovieName = record.get("DescriptionMovieName")

            Movie = GroupManager.getObject(DescriptionGroupName, DescriptionMovieName)

            param = NotebookDescriptionManager.DescriptionEntry(DescriptionTextID, Movie)
            NotebookDescriptionManager.s_descriptions[NoteID] = param
            pass

        pass

    @staticmethod
    def getDescription(id):
        if NotebookDescriptionManager.hasDescription(id) is False:
            return None
            pass

        record = NotebookDescriptionManager.s_descriptions[id]
        return record
        pass

    @staticmethod
    def hasDescription(id):
        if id not in NotebookDescriptionManager.s_descriptions:
            Trace.log("NotebookDescriptionManager", 0,
                      "NotebookDescriptionManager.hasDescription invalid ID, maybe forgot to add in some xls")
            return False
            pass

        return True
        pass

    @staticmethod
    def getAllDescriptions():
        return NotebookDescriptionManager.s_descriptions
        pass

    pass
