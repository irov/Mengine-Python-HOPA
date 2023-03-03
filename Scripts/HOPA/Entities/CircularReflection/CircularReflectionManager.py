from Foundation.DatabaseManager import DatabaseManager


class CircularReflectionManager(object):
    collections = {
        "Movie_Circle1": {
            "Slot1_N": ["Slot1_P1", "Slot1_P2"],
            "Slot2_N": ["Slot2_P1"],
            "Slot3_N": ["Slot3_P1", "Slot3_P2"],
            "Slot4_N": ["Slot4_P1"],
        },
        "Movie_Circle2": {
            "Slot1_N": ["Slot1_P1"],
            "Slot2_N": ["Slot2_P1"],
            "Slot3_N": ["Slot3_P1"],
            "Slot4_N": ["Slot4_P1"],
            "Slot5_N": ["Slot5_P1"],
            "Slot6_N": ["Slot6_P1"],
        },
        "Movie_Circle3": {
            "Slot1_N": ["Slot1_P1", "Slot1_P2"],
            "Slot2_N": ["Slot2_P1", "Slot2_P2"],
            "Slot3_N": ["Slot3_P1", "Slot3_P2"],
            "Slot4_N": ["Slot4_P1", "Slot4_P2"],
            "Slot5_N": ["Slot5_P1", "Slot5_P2"],
            "Slot6_N": ["Slot6_P1", "Slot6_P2"],
            "Slot7_N": ["Slot7_P1", "Slot7_P2"],
            "Slot8_N": ["Slot8_P1", "Slot8_P2"],
        },
        "Movie_Circle4": {
            'Slot8_N': ['Slot8_P'],
            'Slot1_N': ['Slot1_P'],
            'Slot7_N': ['Slot7_P'],
            'Slot5_N': ['Slot5_P'],
            'Slot2_N': ['Slot2_P'],
            'Slot9_N': ['Slot9_P'],
            'Slot6_N': ['Slot6_P'],
            'Slot4_N': ['Slot4_P'],
            'Slot3_N': ['Slot3_P']
        },
        "Movie_Receiver": {
            "Slot1_N": [],
            "Slot2_N": [],
            "Slot3_N": [],
            "Slot4_N": [],
            "Slot5_N": [],
            "Slot6_N": [],
            "Slot7_N": [],
        }
    }

    sub_movies = {
        "Movie_Circle1": ['C1_1', 'C1_2', 'C1_3', 'C1_4'],
        "Movie_Circle2": ['C2_1', 'C2_2', 'C2_3', 'C2_4', 'C2_5', 'C2_6'],
        "Movie_Circle3": ['C3_1', 'C3_2', 'C3_3', 'C3_4', 'C3_5', 'C3_6', 'C3_7', 'C3_8'],
        "Movie_Circle4": ['C4_1', 'C4_2', 'C4_3', 'C4_4', 'C4_5', 'C4_6', 'C4_7', 'C4_8'],
        "Movie_Receiver": ['C5_1', 'C5_2', 'C5_3', 'C5_4', 'C5_5', 'C5_6', 'C5_7', 'C5_8'],
    }

    subMap = {
        "Movie_Circle1": {
            "Slot1_N": "C1_1",
            "Slot2_N": "C1_2",
            "Slot3_N": "C1_3",
            "Slot4_N": "C1_4",
        },
        "Movie_Circle2": {
            "Slot1_N": "C2_2",
            "Slot2_N": "C2_1",
            "Slot3_N": "C2_6",
            "Slot4_N": "C2_5",
            "Slot5_N": "C2_3",
            "Slot6_N": "C2_4",
        },
        "Movie_Circle3": {
            "Slot1_N": "C3_4",
            "Slot2_N": "C3_5",
            "Slot3_N": "C3_1",
            "Slot4_N": "C3_8",
            "Slot5_N": "C3_7",
            "Slot6_N": "C3_6",
            "Slot7_N": "C3_3",
            "Slot8_N": "C3_2",
        },
        "Movie_Circle4": {
            "Slot1_N": "C4_2",
            "Slot2_N": "C4_3",
            "Slot3_N": "C4_4",
            "Slot4_N": "C4_5",
            "Slot5_N": "C4_6",
            "Slot6_N": "C4_7",
            "Slot7_N": "C4_8",
            "Slot8_N": "C4_1",
        },
        "Movie_Receiver": {
            "Slot1_N": "C5_4",
            "Slot2_N": "C5_3",
            "Slot3_N": "C5_2",
            "Slot4_N": "C5_1",
            "Slot5_N": "C5_7",
            "Slot6_N": "C5_6",
            "Slot7_N": "C5_5",
        },
    }

    enigmas_data = {}
    TraceName = "CircularReflectionManager"

    class MapOrientedDocument(object):

        def __init__(self):
            self.collection = {}
            self.subMap = {}
            pass

        def getCollection(self):
            return self.collection
            pass

        def getSubMap(self):
            return self.subMap
            pass

        def insert(self, MovieName, slotInput, subMovie, slotOutputsList):
            if isinstance(slotOutputsList, list) is False:
                Trace.log("Manager", 0, "slotOutputsList must be a list")
                return
                pass

            slotToSubRelation = {slotInput: subMovie}
            if MovieName in self.subMap:
                nestedDict = self.subMap[MovieName]
                nestedDict.update(slotToSubRelation)
                pass
            else:
                self.subMap[MovieName] = slotToSubRelation
                pass

            slotInputToOutputRelation = {slotInput: slotOutputsList}
            if MovieName in self.collection:
                nestedDict = self.collection[MovieName]
                nestedDict.update(slotInputToOutputRelation)
                pass
            else:
                self.collection[MovieName] = nestedDict
                pass
            pass

    @staticmethod
    def onFinalize():
        CircularReflectionManager.enigmas_data = {}
        pass

    @staticmethod
    def load(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for values in records:
            objectName = values.get("EnigmaName")
            if objectName == "":
                continue
            collectionName = values.get("Collection")
            CircularReflectionManager.loadCollection(module, objectName, collectionName)
            pass
        pass

    @staticmethod
    def loadCollection(enigmaName, param):
        dataStoreInstance = CircularReflectionManager.MapOrientedDocument()
        CircularReflectionManager.enigmas_data[enigmaName] = dataStoreInstance
        records = DatabaseManager.getDatabaseRecords(param)

        for record in records:
            movie = record.get("Movie")
            slot_input = record.get("Slot_Negative")
            submovie = record.get("Submovie")
            slot_outputs = record.get("Slot_Positive")
            dataStoreInstance.insert(movie, slot_input, submovie, slot_outputs)
            pass
        pass

    @staticmethod
    def getCollection(enigmaName):
        if enigmaName not in CircularReflectionManager.enigmas_data:
            Trace.log(CircularReflectionManager.TraceName, 0,
                      "%s.getCollection: invalid param %s" % (CircularReflectionManager.TraceName, enigmaName))
            return
            pass
        data = CircularReflectionManager.enigmas_data[enigmaName]
        collection = data.getCollection()
        return collection
        pass

    @staticmethod
    def getSubMap(enigmaName):
        if enigmaName not in CircularReflectionManager.enigmas_data:
            Trace.log(CircularReflectionManager.TraceName, 0,
                      "%s.getCollection: invalid param %s" % (CircularReflectionManager.TraceName, enigmaName))
            return

        data = CircularReflectionManager.enigmas_data[enigmaName]
        map = data.getSubMap()
        return map
