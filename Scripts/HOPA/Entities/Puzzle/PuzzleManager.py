from Foundation.DatabaseManager import DatabaseManager


class PuzzleManager(object):
    s_puzzles = {}

    class PuzzleElement(object):
        def __init__(self, item, place, sprite):
            self.itemName = item
            self.placeObjectName = place
            self.spriteEnableName = sprite
            pass

        def getItemName(self):
            return self.itemName
            pass

        def getPlaceName(self):
            return self.placeObjectName
            pass

        def getSprite(self):
            return self.spriteEnableName
            pass

        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            CollectionParam = record.get("Collection")

            PuzzleManager.loadPuzzle(module, Name, CollectionParam)
            pass
        return True
        pass

    @staticmethod
    def loadPuzzle(module, name, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        puzzle_list = []
        for record in records:
            ItemName = record.get("PickItemName")
            PlaceName = record.get("PlaceItemName")
            SpriteName = record.get("SpriteName")

            element = PuzzleManager.PuzzleElement(ItemName, PlaceName, SpriteName)
            puzzle_list.append(element)
            pass
        PuzzleManager.s_puzzles[name] = puzzle_list
        pass

    @staticmethod
    def getPuzzle(name):
        if name not in PuzzleManager.s_puzzles:
            return None
            pass
        puzzle = PuzzleManager.s_puzzles[name]
        return puzzle
        pass

    @staticmethod
    def hasPuzzle(name):
        if name not in PuzzleManager.s_puzzles:
            Trace.log("PuzzleManager", 0, "PuzzleManager.getPuzzle: not found puzzle %s" % (name))
            return False
        return True
        pass
