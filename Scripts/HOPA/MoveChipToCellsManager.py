from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class MoveChipToCellsManager(Manager):
    s_puzzles = {}

    class MoveChipToCellsParam(object):
        def __init__(self, ChipName, cellParams, bordersParam):
            self.ChipName = ChipName
            self.CellParams = cellParams
            self.BorderParams = bordersParam
            pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ChipName	CellParam	BordersParam
            '''
            EnigmaName = record.get('EnigmaName')
            ChipName = record.get('ChipName')
            CellParam = record.get('CellParam')
            BordersParam = record.get('BordersParam')

            result = MoveChipToCellsManager.addParam(EnigmaName, module, ChipName, CellParam, BordersParam)

            if result is False:
                error_msg = "MoveChipToCellsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipName, CellParam, BordersParam):
        if EnigmaName in MoveChipToCellsManager.s_puzzles:
            error_msg = "MoveChipToCellsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Cell ------------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, CellParam)
        cellParams = {}
        if records is None:
            error_msg = "MoveChipToCellsManager cant find Cell database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                Cell	CellUp	NumOfCells	[CellsWithDeep]

            '''
            Cell = record.get('Cell')
            CellUp = record.get('CellUp')
            StartCell = record.get('StartCell')
            FinishCell = record.get('FinishCell')
            NumOfCells = record.get('NumOfCells')
            CellsWithDeep = record.get('CellsWithDeep')

            cellParams['Cell'] = Cell
            cellParams['CellUp'] = CellUp
            cellParams['StartCell'] = StartCell
            cellParams['FinishCell'] = FinishCell
            cellParams['NumOfCells'] = NumOfCells
            cellParams['CellsWithDeep'] = CellsWithDeep

        # ==============================================================================================================

        # -------------- Borders ---------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, BordersParam)
        bordersParam = []
        if records is None:
            error_msg = "MoveChipToCellsManager cant find Borders database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                numOfBorders	[finishAreaName]

            '''
            # numOfBorders = record.get('numOfBorders')
            # finishAreaName = record.get('finishAreaName')
            #
            # bordersParam['numOfBorders'] = numOfBorders
            # bordersParam['finishAreaName'] = finishAreaName

            cell_1 = record.get('cell_1')
            cell_2 = record.get('cell_2')
            bordersParam.append((cell_1, cell_2))

        # ==============================================================================================================
        # print bordersParam
        new_param = MoveChipToCellsManager.MoveChipToCellsParam(ChipName, cellParams, bordersParam)
        MoveChipToCellsManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return MoveChipToCellsManager.s_puzzles.get(EnigmaName)
