from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class OpenJournalManager(object):
    s_objects = {}

    @staticmethod
    def loadData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            DemonName = record.get("DemonName")
            GroupName = record.get("GroupName")
            CollectionParam = record.get("Collection")

            demon = GroupManager.getObject(GroupName, DemonName)

            states = OpenJournalManager.loadCollection(module, CollectionParam, demon)

            OpenJournalManager.s_objects[demon] = states
            pass

        pass

    @staticmethod
    def loadCollection(module, param, demon):
        records = DatabaseManager.getDatabaseRecords(module, param)
        states = {}

        for record in records:
            State = record.get("State")
            MovieName = record.get("MovieName")

            movie = demon.getObject(MovieName)
            states[State] = movie
            pass
        return states
        pass

    @staticmethod
    def getData(demon):
        if OpenJournalManager.hasData(demon) is False:
            return None
            pass
        record = OpenJournalManager.s_objects[demon]
        return record
        pass

    @staticmethod
    def hasData(demon):
        if demon not in OpenJournalManager.s_objects:
            Trace.log("OpenJournalManager", 0, "OpenJournalManager.hasData invalid param demon %s" % (demon.getName()))
            return False
            pass
        return True
        pass

    pass
