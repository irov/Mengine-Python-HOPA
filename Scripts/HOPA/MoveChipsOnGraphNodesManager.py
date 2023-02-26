from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class MoveChipsOnGraphNodesParam(object):
    def __init__(self, nodes, move_time):
        self.nodes = nodes
        self.move_time = move_time

class MoveChipsOnGraphNodesManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ParamGraph	ChipMoveTime
            '''
            enigma_name = record.get('EnigmaName')
            param_graph = record.get('ParamGraph')
            move_time = record.get('ChipMoveTime')

            result = MoveChipsOnGraphNodesManager.addParam(enigma_name, module, param_graph, move_time)

            if result is False:
                error_msg = "MoveChipsOnGraphNodesManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, param_graph, move_time):
        if enigma_name in MoveChipsOnGraphNodesManager.s_params:
            error_msg = "MoveChipsOnGraphNodesManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, param_graph)
        if records is None:
            error_msg = "MoveChipsOnGraphNodesManager cant find Graph database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        nodes = dict()
        for record in records:
            '''
            Node	Chip	WinChip	[EdgesTo]
            '''
            node = record.get('Node')
            chip = record.get('Chip')
            win_chip = record.get('WinChip')
            edges_to = record.get('EdgesTo')

            nodes[node] = [chip, win_chip, edges_to]

        param = MoveChipsOnGraphNodesParam(nodes, move_time)
        MoveChipsOnGraphNodesManager.s_params[enigma_name] = param
        return True

    @staticmethod
    def getParam(enigma_name):
        return MoveChipsOnGraphNodesManager.s_params.get(enigma_name)