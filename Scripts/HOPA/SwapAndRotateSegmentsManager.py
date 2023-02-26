from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class SwapAndRotateSegmentsManager(Manager):
    s_segments = {}

    class SwapAndRotateSegmentsParam(object):
        def __init__(self, chips_dict):
            self.ChipsParam = chips_dict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	ParamChips          
            '''
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')
            result = SwapAndRotateSegmentsManager.addParam(EnigmaName, module, ParamChips)
            if result is False:
                error_message = "SwapAndRotateSegmentsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_message)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips):
        if EnigmaName in SwapAndRotateSegmentsManager.s_segments:
            error_msg = "SwapAndRotateSegmentsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        chips_dict = {}
        if records is None:
            error_msg = "SwapAndRotateSegmentsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	MovieName	StartPosition	FinishPosition
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')
            StartPosition = record.get('StartPosition')
            FinishPosition = record.get('FinishPosition')

            chips_dict[ChipID] = (MovieName, StartPosition, FinishPosition)
        # ==============================================================================================================

        new_param = SwapAndRotateSegmentsManager.SwapAndRotateSegmentsParam(chips_dict)
        SwapAndRotateSegmentsManager.s_segments[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return SwapAndRotateSegmentsManager.s_segments.get(EnigmaName)