from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ChipsInNetManager(Manager):
    s_puzzles = {}

    class ChipsInNetParam(object):
        def __init__(self, chipDict, Graph):
            self.Chips = chipDict
            self.Graph = Graph
            pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName	ChipsParam	Graph
            '''
            EnigmaName = record.get('EnigmaName')
            ChipsParam = record.get('ChipsParam')
            Graph = record.get('Graph')

            result = ChipsInNetManager.addParam(EnigmaName, module, ChipsParam, Graph)

            if result is False:
                error_msg = "ChipsInNetManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipsParam, Graph):
        if EnigmaName in ChipsInNetManager.s_puzzles:
            error_msg = "ChipsInNetManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipsParam)

        chipDict = {}

        if records is None:
            error_msg = "ChipsInNetManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')
            chipDict[ChipID] = MovieName
        # ==============================================================================================================

        # -------------- Graph -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, Graph)

        graph = {}

        if records is None:
            error_msg = "ChipsInNetManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	[ConnectedChipsID]
            '''
            ChipID = record.get('ChipID')
            ConnecnedChipsID = record.get('ConnectedChipsID')
            graph[ChipID] = ConnecnedChipsID
        # ==============================================================================================================

        new_param = ChipsInNetManager.ChipsInNetParam(chipDict, graph)
        ChipsInNetManager.s_puzzles[EnigmaName] = new_param

        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipsInNetManager.s_puzzles.get(EnigmaName)