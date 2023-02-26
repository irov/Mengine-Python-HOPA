from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class DragTheChainToTheRightPlaceManager(Manager):
    s_puzzles = {}

    class DragTheChainToTheRightPlaceParam(object):
        def __init__(self, graphParam, chipsParam, NumOfSlots, chainParam, winComb, textureName):
            self.Graph = graphParam
            self.Chips = chipsParam
            self.NumOfSlots = NumOfSlots
            self.chainParam = chainParam
            self.winComb = winComb
            self.textureName = textureName

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	GraphParam	ChipsParam	NumOfSlots	ChainParam	MasterChain	[winSlotsForMasterChain]

            '''
            EnigmaName = record.get('EnigmaName')
            GraphParam = record.get('GraphParam')
            ChipsParam = record.get('ChipsParam')
            NumOfSlots = record.get('NumOfSlots')
            TextureName = record.get('TextureName')
            ChainParam = record.get('ChainParam')
            MasterChain = record.get('MasterChain')
            winSlotsForMasterChain = record.get('winSlotsForMasterChain')
            winComb = (MasterChain, winSlotsForMasterChain)

            result = DragTheChainToTheRightPlaceManager.addParam(EnigmaName, module, GraphParam, ChipsParam, NumOfSlots, ChainParam, winComb, TextureName)
            if result is False:
                error_msg = "MoveChipToCellsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, GraphParam, ChipsParam, NumOfSlots, ChainParam, winComb, TextureName):
        if EnigmaName in DragTheChainToTheRightPlaceManager.s_puzzles:
            error_msg = "MoveChipToCellsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Graph -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, GraphParam)
        graphParam = {}
        if records is None:
            error_msg = "DragTheChainToTheRightPlaceManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                Key	Value	Exception

            '''
            Key = record.get('Key')
            graphParam[Key] = []
        for record in records:
            '''
                Key	Value	Exception

            '''
            Key = record.get('Key')
            Value = record.get('Value')
            Exception = record.get('Exception')
            graphParam[Key].append((Value, Exception))
        # ==============================================================================================================

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipsParam)
        chipsParam = {}
        if records is None:
            error_msg = "DragTheChainToTheRightPlaceManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChainID	ChipType	SlotID
            '''
            ChainID = record.get('ChainID')
            chipsParam[ChainID] = {}

        for record in records:
            ChainID = record.get('ChainID')
            ChipType = record.get('ChipType')
            SlotID = record.get('SlotID')
            chipsParam[ChainID][SlotID] = ChipType

        # ==============================================================================================================

        # -------------- ChainParam ------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChainParam)
        chainParam = {}
        if records is None:
            error_msg = "DragTheChainToTheRightPlaceManager cant find ChainParam database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChainName	[Order]

            '''
            ChainName = record.get('ChainName')
            Order = record.get('Order')
            chainParam[ChainName] = Order
        # ==============================================================================================================

        new_param = DragTheChainToTheRightPlaceManager.DragTheChainToTheRightPlaceParam(graphParam, chipsParam, NumOfSlots, chainParam, winComb, TextureName)
        DragTheChainToTheRightPlaceManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return DragTheChainToTheRightPlaceManager.s_puzzles.get(EnigmaName)