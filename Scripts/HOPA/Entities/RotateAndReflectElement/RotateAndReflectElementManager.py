from Foundation.DatabaseManager import DatabaseManager


class RotateAndReflectElementManager(object):
    s_object = {}

    class Data(object):
        def __init__(self, swap, element, socket):
            self.swap = swap
            self.socket = socket
            self.element = element
            pass

        def getSwap(self):
            return self.swap
            pass

        def getSocket(self):
            return self.socket
            pass

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
            pass

        def getStartPos(self):
            return self.start
            pass

        def getWinPos(self):
            return self.win
            pass

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
        pass

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
        pass

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
        pass

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
        pass

    @staticmethod
    def getData(name):
        if RotateAndReflectElementManager.hasData(name) is False:
            return None
            pass
        data = RotateAndReflectElementManager.s_object[name]
        return data
        pass

    @staticmethod
    def hasData(name):
        if name not in RotateAndReflectElementManager.s_object:
            Trace.log("Manager", 0, "RotateAndReflectElementManager.hasData invalid param -->%s" % (name))
            return False
            pass
        return True
        pass

    pass
