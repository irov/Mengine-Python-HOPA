from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class TurnBasedStrategyGoManager(Manager):
    s_params = {}

    class TurnBasedStrategyGoManagerLevelParam(object):
        def __init__(self, level_id, content_name, place_number, start_enemy_slots, start_players_slots):
            self.level_id = level_id
            self.content_name = content_name
            self.place_number = place_number
            self.start_enemy_slots = [3, 9]
            self.start_players_slots = [16, 22]

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName	Levels
            '''
            enigma_name = record.get('EnigmaName')
            levels = record.get('Levels')

            result = TurnBasedStrategyGoManager.addParam(enigma_name, module, levels)

            if result is False:
                error_msg = "TurnBasedStrategyGoManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, levels):
        if enigma_name in TurnBasedStrategyGoManager.s_params:
            error_msg = "TurnBasedStrategyGoManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, levels)

        levels_dict = {}

        if records is None:
            error_msg = "TurnBasedStrategyGoManager cant find Levels database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            LevelID	ContentName	PlaceNumber	[StartEnemyChipsSlots]	[StartPlayerChipsSlots]
            '''
            level_id = record.get('LevelID')
            content_name = record.get('ContentName')
            place_number = record.get('PlaceNumber')
            start_enemy_chips_slots = record.get('StartEnemyChipsSlots')
            start_player_chips_slots = record.get('StartPlayerChipsSlots')

            param = TurnBasedStrategyGoManager.TurnBasedStrategyGoManagerLevelParam(
                level_id, content_name, place_number, start_enemy_chips_slots, start_player_chips_slots)
            levels_dict[level_id] = param

        TurnBasedStrategyGoManager.s_params[enigma_name] = levels_dict
        return True

    @staticmethod
    def getParams(enigma_name):
        return TurnBasedStrategyGoManager.s_params.get(enigma_name)
