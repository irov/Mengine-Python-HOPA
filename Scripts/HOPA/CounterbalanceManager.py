from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class CounterbalanceParam(object):
    def __init__(self, matrix_size, distance, first_pos, hotspot_size, rope_hand, wheels, teams, reward_movie,
                 skip_ways, continue_chain_mod):
        self.matrix_size = matrix_size
        self.distance = distance
        self.first_pos = first_pos
        self.hotspot_size = hotspot_size
        self.rope_hand = rope_hand
        self.wheels = wheels
        self.teams = teams
        self.reward_movie = reward_movie
        self.skip_ways = skip_ways
        self.continue_chain_mod = continue_chain_mod


class CounterbalanceManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	MatrixSizeX	MatrixSizeY	DistanceX	DistanceY	
            UpperLeftPosX	UpperLeftPosY	HotSpotSize
            RopeHand	WheelParam	TeamParam	
            '''
            enigma_name = record.get('EnigmaName')
            matrix_size = (record.get("MatrixSizeX"), record.get("MatrixSizeY"))
            distance = (record.get("DistanceX"), record.get("DistanceY"))
            first_pos = (record.get("UpperLeftPosX"), record.get("UpperLeftPosY"))
            hotspot_size = record.get("HotSpotSize")
            rope_hand = record.get("RopeHand")
            wheel_xlsx = record.get("WheelParam")
            team_xlsx = record.get("TeamParam")
            skip_xlsx = record.get("SkipParam")
            reward_movie = record.get("RewardMovie")
            continue_chain_mod = bool(record.get("ContinueChain", False))

            result = CounterbalanceManager.addParam(enigma_name, module, matrix_size, distance, first_pos, hotspot_size,
                                                    rope_hand, wheel_xlsx, team_xlsx, reward_movie, skip_xlsx,
                                                    continue_chain_mod)

            if result is False:
                error_msg = "CounterbalanceManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, matrix_size, distance, first_pos, hotspot_size, rope_hand, wheel_xlsx, team_xlsx,
                 reward_movie, skip_xlsx, continue_chain_mod):
        wheels = list()
        teams = dict()
        skip_ways = dict()

        if enigma_name in CounterbalanceManager.s_params:
            error_msg = "CounterbalanceManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, wheel_xlsx)
        if records is None:
            error_msg = "CounterbalanceManager cant find WheelParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            Index	Prototype
            '''
            wheel_prototype = record.get("Prototype", None)
            wheels.append(wheel_prototype)

        if len(wheels) != matrix_size[0] * matrix_size[1]:
            error_msg = "CounterbalanceManager {} wheels number is not equal to MatrixSizeX * MatrixSizeY".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, team_xlsx)
        if records is None:
            error_msg = "CounterbalanceManager cant find TeamParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            Team	TeamEffectPrototype KingPrototype	QueenPrototype	
            RopePrototype	RopeHandSprite	WheelPrototypeSprite
            '''
            team_param = dict()
            team_name = record.get('Team')
            team_param['TeamEffectPrototype'] = record.get('TeamEffectPrototype')
            team_param['KingPrototype'] = record.get('KingPrototype')
            team_param['QueenPrototype'] = record.get('QueenPrototype')
            team_param['RopePrototype'] = record.get('RopePrototype')
            team_param['RopeHandSprite'] = record.get('RopeHandSprite')
            team_param['WheelPrototypeSprite'] = record.get('WheelPrototypeSprite')
            teams[team_name] = team_param

        records = DatabaseManager.getDatabaseRecords(module, skip_xlsx)
        if records is None:
            error_msg = "CounterbalanceManager cant find SkipParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            Purple  Blue   Yellow   Red  Green  
            '''
            team_name = record.get("TeamName")
            wheel_name = record.get("WheelName")

            team_wheels = skip_ways.get(team_name)
            if team_wheels is None:
                ls = [wheel_name]
                skip_ways[team_name] = ls
            else:
                team_wheels.append(wheel_name)
                skip_ways[team_name] = team_wheels

        param = CounterbalanceParam(matrix_size, distance, first_pos, hotspot_size, rope_hand, wheels, teams,
                                    reward_movie, skip_ways, continue_chain_mod)

        CounterbalanceManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return CounterbalanceManager.s_params.get(enigma_name)
