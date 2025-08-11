from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class ManaManager(Manager):
    s_objects = {}

    class ManaData(object):
        def __init__(self, idle, hide, show, down, update):
            self.idle = idle
            self.hide = hide
            self.show = show
            self.down = down
            self.update = update
            pass

        def getUpdate(self):
            return self.update

        def getIdle(self):
            return self.idle

        def getHide(self):
            return self.hide

        def getShow(self):
            return self.show

        def getDown(self):
            return self.down

    @staticmethod
    def _onFinalize():
        ManaManager.s_objects = {}
        pass

    @staticmethod
    def loadMana(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            GroupName = values.get("GroupName")
            ObjectName = values.get("ObjectName")
            ManaDemon = GroupManager.getObject(GroupName, ObjectName)

            MovieUpdateName = values.get("MovieUpdateName")
            UpdateMovie = ManaDemon.getObject(MovieUpdateName)

            IdleMovie = None
            HideMovie = None
            ShowMovie = None
            DownMovie = None

            IdleMovieName = values.get("MovieIdleName")
            if IdleMovieName is not None:
                IdleMovie = ManaDemon.getObject(IdleMovieName)
                pass

            HideMovieName = values.get("MovieHideName")
            if HideMovieName is not None:
                HideMovie = ManaDemon.getObject(HideMovieName)
                pass

            ShowMovieName = values.get("MovieShowName")
            if ShowMovieName is not None:
                ShowMovie = ManaDemon.getObject(ShowMovieName)
                pass

            DownMovieName = values.get("MovieDownName")
            if DownMovieName is not None:
                DownMovie = ManaDemon.getObject(DownMovieName)
                pass

            Mana = ManaManager.ManaData(IdleMovie, HideMovie, ShowMovie, DownMovie, UpdateMovie)

            ManaManager.s_objects[ManaDemon] = Mana
            pass
        pass

    @staticmethod
    def getManaData(object):
        if ManaManager.hasManaData(object) is False:
            return None
            pass
        record = ManaManager.s_objects[object]
        return record
        pass

    @staticmethod
    def hasManaData(object):
        if object not in ManaManager.s_objects:
            Trace.log("ManaManager", 0, "ManaManager.hasManaData: : invalid param")
            return False
            pass
        return True
        pass

    pass
