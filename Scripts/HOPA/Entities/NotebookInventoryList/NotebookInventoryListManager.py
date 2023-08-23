from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager


class NotebookInventoryListManager(Manager):
    s_showEntries = {}
    s_textes = {}
    s_trigger = None

    class TriggerData(object):
        def __init__(self, obj, group, autoEnable, isClick, ClickOnButton):
            self.obj = obj
            self.group = group
            self.autoEnable = autoEnable
            self.isClick = isClick
            self.ClickOnButton = ClickOnButton
            pass

        def getObjectName(self):
            return self.obj
            pass

        def getGroupName(self):
            return self.group
            pass

        def getAutoEnable(self):
            return self.autoEnable
            pass

        def getIsClick(self):
            return self.isClick
            pass

        def getClickOnButton(self):
            return self.ClickOnButton
            pass

    class ShowEntry(object):
        def __init__(self, showMovie, idleMovie, hideMovie):
            self.showMovie = showMovie
            self.idleMovie = idleMovie
            self.hideMovie = hideMovie
            pass

        def getShowMovie(self):
            return self.showMovie
            pass

        def getIdleMovie(self):
            return self.idleMovie
            pass

        def getHideMovie(self):
            return self.hideMovie
            pass

        def onDestroy(self):
            self.showMovie.onDestroy()
            self.idleMovie.onDestroy()
            self.hideMovie.onDestroy()
            pass

        pass

    @staticmethod
    def _onInitialize(*args):
        pass

    @staticmethod
    def _onFinalize():
        for entry in NotebookInventoryListManager.s_showEntries.itervalues():
            entry.onDestroy()
            pass

        NotebookInventoryListManager.s_showEntries = {}
        NotebookInventoryListManager.s_textes = {}
        NotebookInventoryListManager.s_trigger = None
        return False
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ShowModuleName = record.get("ShowModuleName")
            ShowTextModuleName = record.get("ShowTextModuleName")
            TriggerObjectName = record.get("ShowTriggerObject")
            TriggerObjectGroup = record.get("ShowTriggerGroup")
            TriggerIsClick = bool(int(record.get("isClick", 0)))
            TriggerAutoEnable = bool(int(record.get("AutoEnable", 1)))
            TriggerClickOnButton = bool(int(record.get("ClickOnButton", 0)))

            trigger = NotebookInventoryListManager.TriggerData(TriggerObjectName, TriggerObjectGroup,
                                                               TriggerAutoEnable, TriggerIsClick, TriggerClickOnButton)
            NotebookInventoryListManager.s_trigger = trigger
            NotebookInventoryListManager.addShowMovies(module, ShowModuleName)
            NotebookInventoryListManager.addTextes(module, ShowTextModuleName)
            pass

        return True
        pass

    @staticmethod
    def addTextes(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            noteid = record.get("NoteID")
            noteTextId = record.get("NoteTextID")
            NotebookInventoryListManager.s_textes[noteid] = noteTextId
        pass

    @staticmethod
    def getText(value):
        if NotebookInventoryListManager.hasText(value) is False:
            return None
            pass

        record = NotebookInventoryListManager.s_textes[value]
        return record
        pass

    @staticmethod
    def hasText(value):
        if value not in NotebookInventoryListManager.s_textes:
            Trace.log("NotebookInventoryListManager", 0,
                      "NotebookInventoryListManager.hasText invalid value %s, maybe forgot to add in xls" % (value,))
            return False
            pass

        return True
        pass

    @staticmethod
    def addShowMovies(module, param):
        def Setup_Movie(GroupName, ProtName, Value):
            MovieName = ProtName + "_" + str(Value)
            Movie = GroupManager.generateObjectUnique(MovieName, GroupName, ProtName)

            if Movie is None:
                return None

            Position = Movie.getPosition()
            difference = DefaultManager.getDefaultFloat("TasksShowInterval", 100.0)
            Position = (Position[0], Position[1] + difference * (Value - 1), Position[2])
            Movie.setPosition(Position)

            Movie.setEnable(False)
            return Movie

        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Value = record.get("Value")
            ShowGroupName = record.get("ShowGroupName")
            ShowName = record.get("ShowName")
            IdleGroupName = record.get("IdleGroupName")
            IdleName = record.get("IdleName")
            HideGroupName = record.get("HideGroupName")
            HideName = record.get("HideName")

            ShowMovie = Setup_Movie(ShowGroupName, ShowName, Value)

            if ShowMovie is None:
                Trace.log("NotebookInventoryListManager", 0,
                          "NotebookInventoryListManager.addShowMovies invalid %s:%s, maybe it doesn't exist" % (ShowGroupName, ShowName,))
                return False
                pass

            IdleMovie = Setup_Movie(IdleGroupName, IdleName, Value)
            HideMovie = Setup_Movie(HideGroupName, HideName, Value)

            entry = NotebookInventoryListManager.ShowEntry(ShowMovie, IdleMovie, HideMovie)
            NotebookInventoryListManager.s_showEntries[Value] = entry
            pass
        pass

    @staticmethod
    def getShowEntry(value):
        if NotebookInventoryListManager.hasShowEntry(value) is False:
            return None
            pass

        record = NotebookInventoryListManager.s_showEntries[value]
        return record
        pass

    @staticmethod
    def hasShowEntry(value):
        if value not in NotebookInventoryListManager.s_showEntries:
            # Trace.log("NotebookInventoryListManager", 0 , "NotebookInventoryListManager.hasShowEntry invalid value '%s', maybe forgot to add in xls"%(value, ))
            Trace.log("Manager", 0, " if value not in NotebookInventoryListManager.s_showEntries")
            return False
            pass

        return True
        pass

    @staticmethod
    def getAllShowEntry():
        return NotebookInventoryListManager.s_showEntries
        pass

    @staticmethod
    def getTriggerData():
        return NotebookInventoryListManager.s_trigger
