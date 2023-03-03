from Foundation.DatabaseManager import DatabaseManager


class SameElementsManager(object):
    s_collections = {}
    s_buttonsChange = {}
    s_buttonsCollection = {}

    class Collection(object):
        def __init__(self, movieName):
            self.slots = {}
            self.movieName = movieName
            pass

        def getMovieName(self):
            return self.movieName
            pass

        def addSlot(self, slotID, startElementName):
            self.slots[slotID] = startElementName
            pass

        def getSlots(self):
            return self.slots
            pass

        pass

    class ButtonChange(object):
        def __init__(self, collection1ID, slot1ID, collection2ID, slot2ID):
            self.collection1ID = collection1ID
            self.slot1ID = slot1ID
            self.collection2ID = collection2ID
            self.slot2ID = slot2ID
            pass

        def getCollectionID1(self):
            return self.collection1ID
            pass

        def getCollectionID2(self):
            return self.collection2ID
            pass

        def getSlot1ID(self):
            return self.slot1ID
            pass

        def getSlot2ID(self):
            return self.slot2ID
            pass

        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Collections = record.get("Collections")
            ButtonsChange = record.get("ButtonsChange")
            ButtonsCollection = record.get("ButtonsCollection")

            SameElementsManager.loadCollections(module, Collections, EnigmaName)
            SameElementsManager.loadButtonsChange(module, ButtonsChange, EnigmaName)
            SameElementsManager.loadButtonsCollection(module, ButtonsCollection, EnigmaName)
            pass

        return True
        pass

    @staticmethod
    def loadCollections(module, name, enigmaName):
        records = DatabaseManager.getDatabaseRecords(module, name)

        SameElementsManager.s_collections[enigmaName] = {}

        for record in records:
            CollectionID = record.get("CollectionID")
            MovieName = record.get("MovieName")
            SlotID = record.get("SlotID")
            StartElement = record.get("StartElement")
            if CollectionID not in SameElementsManager.s_collections[enigmaName].keys():
                Collection = SameElementsManager.Collection(MovieName)
                SameElementsManager.s_collections[enigmaName][CollectionID] = Collection
                pass
            else:
                Collection = SameElementsManager.s_collections[enigmaName][CollectionID]
                pass

            Collection.addSlot(SlotID, StartElement)
            pass
        pass

    @staticmethod
    def loadButtonsChange(module, name, enigmaName):
        records = DatabaseManager.getDatabaseRecords(module, name)

        SameElementsManager.s_buttonsChange[enigmaName] = {}

        for record in records:
            ButtonName = record.get("ButtonName")
            Collection1ID = record.get("Collection1ID")
            Slot1ID = record.get("Slot1ID")
            Collection2ID = record.get("Collection2ID")
            Slot2ID = record.get("Slot2ID")

            ButtonChange = SameElementsManager.ButtonChange(Collection1ID, Slot1ID, Collection2ID, Slot2ID)
            SameElementsManager.s_buttonsChange[enigmaName][ButtonName] = ButtonChange
            pass
        pass

    @staticmethod
    def loadButtonsCollection(module, name, enigmaName):
        records = DatabaseManager.getDatabaseRecords(module, name)

        SameElementsManager.s_buttonsCollection[enigmaName] = {}

        for record in records:
            ButtonName = record.get("ButtonName")
            CollectionID = record.get("CollectionID")

            SameElementsManager.s_buttonsCollection[enigmaName][ButtonName] = CollectionID
            pass
        pass

    @staticmethod
    def getButtonCollections(enigmaName):
        return SameElementsManager.s_buttonsCollection[enigmaName]
        pass

    @staticmethod
    def getCollections(enigmaName):
        return SameElementsManager.s_collections[enigmaName]
        pass

    @staticmethod
    def getButtonsChange(enigmaName):
        return SameElementsManager.s_buttonsChange[enigmaName]
        pass

    pass
