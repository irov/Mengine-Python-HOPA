from Foundation.DatabaseManager import DatabaseManager

class PuzzleDragDropManager(object):
    s_objects = {}

    class PuzzleDragDrop(object):
        def __init__(self, elements, Linked, winState):
            self.elements = elements
            self.winCase = winState
            self.LinkedItems = Linked  # dictinary
            pass

        def getLinks(self):
            return self.LinkedItems
            pass
        pass

    @staticmethod
    def onFinalize():
        PuzzleDragDropManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("Name")
            if objectName == "":
                continue

            collectionName = values.get("Collection")

            PuzzleDragDropManager.loadPuzzleDragDropCollection(objectName, module, collectionName)
            pass

        return True
        pass

    @staticmethod
    def loadPuzzleDragDropCollection(objectName, module, collectionName):
        elements = []
        winCase = []
        LinkItems = {}

        records = DatabaseManager.getDatabaseRecords(module, collectionName)

        for values in records:
            pickItemName = values.get("PickItemName")
            placeItemName = values.get("PlaceItemName")
            winState = values.get("WinCase")
            Linked = values.get("LinkedPart")

            LinkItems[pickItemName] = []
            if Linked is not None:
                LinkItems[pickItemName] = Linked
                pass

            if winState is not None:
                winCase.append(winState)
                pass

            elements.append((pickItemName, placeItemName))
            pass

        Object = PuzzleDragDropManager.PuzzleDragDrop(elements, LinkItems, winCase)

        PuzzleDragDropManager.s_objects[objectName] = Object

        pass

    @staticmethod
    def getPuzzleDragDrop(name):
        if PuzzleDragDropManager.hasPuzzleDragDrop(name) is False:
            return None
            pass

        return PuzzleDragDropManager.s_objects[name]
        pass

    @staticmethod
    def hasPuzzleDragDrop(name):
        if name not in PuzzleDragDropManager.s_objects.keys():
            return False
            pass

        return True
        pass

    pass

pass