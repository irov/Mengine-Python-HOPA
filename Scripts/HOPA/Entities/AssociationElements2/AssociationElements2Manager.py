from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class AssociationElements2Manager(Manager):
    s_objects = {}

    class ElementData(object):
        def __init__(self, name, slot, socket, open, close, active):
            self.name = name
            self.slot = slot
            self.socket = socket
            self.open = open
            self.close = close
            self.active = active
            pass

        def getName(self):
            return self.name

        def getSlotName(self):
            return self.slot

        def getSocketName(self):
            return self.socket

        def getOpenMovieName(self):
            return self.open

        def getCloseMovieName(self):
            return self.close

        def getActiveMovieName(self):
            return self.active

    @staticmethod
    def _onInitialize():
        return True

    @staticmethod
    def _onFinalize():
        AssociationElements2Manager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for value in records:
            EnigmaName = value.get("EnigmaName")
            Collection = value.get("Collection")

            data = AssociationElements2Manager.loadCollection(module, Collection)

            AssociationElements2Manager.s_objects[EnigmaName] = data
            pass

        return True

    @staticmethod
    def loadCollection(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        data = []
        for value in records:
            Name = value.get("Name")
            SlotName = value.get("SlotName")
            SocketName = value.get("SocketName")
            OpenMovie = value.get("OpenMovie")
            CloseMovie = value.get("CloseMovie")
            ActiveMovie = value.get("ActiveMovie")

            element = AssociationElements2Manager.ElementData(Name, SlotName, SocketName, OpenMovie, CloseMovie, ActiveMovie)

            data.append(element)
            pass

        return data

    @staticmethod
    def getData(name):
        if AssociationElements2Manager.hasData(name) is False:
            return None
        record = AssociationElements2Manager.s_objects[name]
        return record

    @staticmethod
    def hasData(name):
        if name not in AssociationElements2Manager.s_objects:
            Trace.log("AssociationElements2Manager", 0, "AssociationElements2Manager.hasData invalid mapID %s" % (name))
            return False
        return True
