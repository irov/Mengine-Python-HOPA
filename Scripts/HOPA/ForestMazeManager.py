from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ForestMazeManager(Manager):
    class ForestMazeParam(object):
        class __PlaceParam(object):
            def __init__(self, place_id, chip_type, movie_prototype_name, other_params):
                self.place_id = place_id
                self.chip_type = chip_type
                self.movie_prototype_name = movie_prototype_name
                self.other_params = other_params

                if _DEVELOPMENT is True:
                    self.__assertion_test()

            def __assertion_test(self):
                assert self.place_id is not None, "PlaceID is None"
                assert self.chip_type is not None, "ChipType in Chip {} is None".format(self.place_id)
                assert self.movie_prototype_name is not None, "MoviePrototypeName in Chip {} is None".format(self.place_id)

        def __init__(self, enigma_name, finish_point, enemy_rotate_angle, place_params, rotate_time, player_move_time,
                     neutral_move_time, disable_glow):
            self.enigma_name = enigma_name

            self.finish_point = finish_point
            self.enemy_rotate_angle = enemy_rotate_angle
            self.places = {}
            self.extra = {"RotateTime": rotate_time, "PlayerMoveTime": player_move_time,
                "NeutralMoveTime": neutral_move_time, "DisableFinishGlowAfterReset": disable_glow}

            self.__createPlaces(place_params)

            if _DEVELOPMENT is True:
                self.__assertion_test()

        def __assertion_test(self):
            assert self.enigma_name is not None, "EnigmaName is None"
            assert self.finish_point is not None, "FinishPoint in Enigma {} is None".format(self.enigma_name)
            assert isinstance(self.enemy_rotate_angle, (int, float)), "Enigma {} EnemyRotateAngle is {} but must be int or float".format(self.enigma_name, type(self.enemy_rotate_angle))
            assert self.places != {}, "You don`t register any Place in {}_Places.xlsx".format(self.enigma_name)
            assert self.extra["RotateTime"] > 0, "Enigma {} RotateTime must be positive number".format(self.enigma_name)
            assert self.extra["PlayerMoveTime"] > 0, "Enigma {} PlayerMoveTime must be positive number".format(self.enigma_name)
            assert self.extra["NeutralMoveTime"] > 0, "Enigma {} NeutralMoveTime must be positive number".format(self.enigma_name)
            assert self.extra["DisableFinishGlowAfterReset"] in (1, 0), "Enigma {} DisableFinishGlowAfterReset must be 1 for True or 0 for False".format(self.enigma_name)

        def __createPlaces(self, place_params):
            for place_id, params in place_params.iteritems():
                self.places[place_id] = self.__PlaceParam(place_id, *params)

    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            """
            EnigmaName	FinishPoint	PlacesParam	EnemyRotateAngle
            """
            enigma_name = record.get('EnigmaName')
            finish_point = record.get('FinishPoint')
            places_param = record.get('PlacesParam')
            enemy_rotate_angle = record.get('EnemyRotateAngle')
            rotate_time = record.get('RotateTime', 500)
            player_move_time = record.get('PlayerMoveTime', 1000)
            neutral_move_time = record.get('NeutralMoveTime', 1000)
            disable_glow = record.get('DisableFinishGlowAfterReset', False)

            result = ForestMazeManager.addParam(enigma_name, module, finish_point, enemy_rotate_angle, places_param,
                                                rotate_time, player_move_time, neutral_move_time, disable_glow)
            if result is False:
                error_msg = "ForestMazeManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(enigma_name, module, finish_point, enemy_rotate_angle, places_param, rotate_time, player_move_time,
                 neutral_move_time, disable_glow):
        if enigma_name in ForestMazeManager.s_params:
            error_msg = "ForestMazeManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Places ----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, places_param)
        place_params = {}

        if records is None:
            error_msg = "ForestMazeManager cant find Places database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            """
            PlaceID	ChipType	MoviePrototypeName  [OthersParams]
            """
            place_id = record.get('PlaceID')
            chip_type = record.get('ChipType')
            movie_prototype_name = record.get('MoviePrototypeName')
            other_params = record.get('OthersParams')

            place_params[place_id] = (chip_type, movie_prototype_name, other_params)

        ForestMazeManager.s_params[enigma_name] = ForestMazeManager.ForestMazeParam(enigma_name, finish_point,
                                                                                    enemy_rotate_angle, place_params,
                                                                                    rotate_time, player_move_time,
                                                                                    neutral_move_time, disable_glow)

        return True

    @staticmethod
    def getParam(enigma_name, key=None):
        param = ForestMazeManager.s_params.get(enigma_name)

        if key is not None:
            if "extra" in param.__dict__:
                param = param.extra.get(key, None)
            else:
                param = param.__dict__.get(key, None)

        return param
