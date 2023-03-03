from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class MoveCursorToRightPlacesManager(Manager):
    s_puzzles = {}

    class MoveCursorToRightPlacesParam(object):
        def __init__(self, places_dict, AttachOnCursor):
            self.Places = places_dict
            self.AttachOnCursor = AttachOnCursor

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ParamPlaces	AttachOnCursor
            '''
            EnigmaName = record.get('EnigmaName')
            ParamPlaces = record.get('ParamPlaces')
            AttachOnCursor = record.get('AttachOnCursor')

            result = MoveCursorToRightPlacesManager.addParam(EnigmaName, module, ParamPlaces, AttachOnCursor)

            if result is False:
                error_msg = "MoveCursorToRightPlacesManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, module, ParamPlaces, AttachOnCursor):
        if EnigmaName in MoveCursorToRightPlacesManager.s_puzzles:
            error_msg = "MoveCursorToRightPlacesManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Places ----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, ParamPlaces)
        places_dict = {}

        if records is None:
            error_msg = "MoveCursorToRightPlacesManager cant find Place database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            PlaceID	MovieName
            '''
            PlaceID = record.get('PlaceID')
            MovieName = record.get('MovieName')

            places_dict[PlaceID] = MovieName

        new_param = MoveCursorToRightPlacesManager.MoveCursorToRightPlacesParam(places_dict, AttachOnCursor)
        MoveCursorToRightPlacesManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return MoveCursorToRightPlacesManager.s_puzzles.get(EnigmaName)
