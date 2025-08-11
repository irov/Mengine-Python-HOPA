from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class RotateAndReflectElementManager(Manager):
    s_object = {}

    class Data(object):
        def __init__(self, swap, element, socket):
            self.swap = swap
            self.socket = socket
            self.element = element
            pass

        def getSwap(self):
            return self.swap

        def getSocket(self):
            return self.socket

        def getElement(self):
            return self.element

    class Element(object):
        def __init__(self, sprite, start, win):
            self.sprite = sprite
            self.start = start
            self.win = win
            pass

        def getSprite(self):
            return self.sprite

        def getStartPos(self):
            return self.start

        def getWinPos(self):
            return self.win

    @staticmethod
    def _onFinalize():
        RotateAndReflectElementManager.s_object = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            SwapCollection = record.get("SwapCollection")
            ElementCollection = record.get("ElementCollection")
            SocketCollection = record.get("SocketCollection")

            swapData = RotateAndReflectElementManager.loadSwapData(module, SwapCollection)
            elementData = RotateAndReflectElementManager.loadElementData(module, ElementCollection)
            socketData = RotateAndReflectElementManager.loadSocketData(module, SocketCollection)

            data = RotateAndReflectElementManager.Data(swapData, elementData, socketData)
            RotateAndReflectElementManager.s_object[EnigmaName] = data

        return True

    @staticmethod
    def loadSwapData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        swapData = {}
        for record in records:
            MovieName = record.get("MovieName")
            Slot = record.get("Slot")
            Swap = record.get("Swap")

            swapData[MovieName] = (Slot, Swap)
            pass
        return swapData

    @staticmethod
    def loadElementData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        elementData = {}
        for record in records:
            ElementName = record.get("ElementName")
            Sprite = record.get("Sprite")
            StartSlot = record.get("StartSlot")
            WinSlot = record.get("WinSlot")

            elementData[ElementName] = RotateAndReflectElementManager.Element(Sprite, StartSlot, WinSlot)
            pass
        return elementData

    @staticmethod
    def loadSocketData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        socketData = {}
        for record in records:
            SocketName = record.get("SocketName")
            MovieName = record.get("MovieName")
            socketData[SocketName] = MovieName
            pass
        return socketData

    @staticmethod
    def getData(name):
        if RotateAndReflectElementManager.hasData(name) is False:
            return None
        data = RotateAndReflectElementManager.s_object[name]
        return data

    @staticmethod
    def hasData(name):
        if name not in RotateAndReflectElementManager.s_object:
            Trace.log("Manager", 0, "RotateAndReflectElementManager.hasData invalid param -->%s" % (name))
            return False
        return True
    pass
