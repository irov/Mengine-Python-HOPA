from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ChipDragDropConnectPuzzleManager(Manager):
    s_puzzles = {}

    class ChipDragDropConnectPuzzleParam(object):
        def __init__(self, chips_dict, graph_dict):
            self.chipsDict = chips_dict
            self.graphDict = graph_dict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')
            ParamGraph = record.get('ParamGraph')

            result = ChipDragDropConnectPuzzleManager.addParam(EnigmaName, module, ParamChips, ParamGraph)

            if result is False:
                error_msg = "ChipDragDropConnectPuzzleManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips, ParamGraph):
        if EnigmaName in ChipDragDropConnectPuzzleManager.s_puzzles:
            error_msg = "ChipDragDropConnectPuzzleManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        chips_dict = {}
        if records is None:
            error_msg = "ChipDragDropConnectPuzzleManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')

            chips_dict[ChipID] = MovieName

        records = DatabaseManager.getDatabaseRecords(Module, ParamGraph)
        graph_dict = {}

        if records is None:
            error_msg = "ChipDragDropConnectPuzzleManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            FromChipID	ToChipID	FromConnectionSlot	ToConnectionSlot
            '''
            FromChipID = record.get('FromChipID')
            ToChipID = record.get('ToChipID')
            FromConnectionSlot = record.get('FromConnectionSlot')
            ToConnectionSlot = record.get('ToConnectionSlot')

            graph_dict[(FromChipID, ToChipID)] = (FromConnectionSlot, ToConnectionSlot)

        new_param = ChipDragDropConnectPuzzleManager.ChipDragDropConnectPuzzleParam(chips_dict, graph_dict)
        ChipDragDropConnectPuzzleManager.s_puzzles[EnigmaName] = new_param

        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipDragDropConnectPuzzleManager.s_puzzles.get(EnigmaName)