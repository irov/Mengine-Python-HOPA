from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class StonePyramidsParam(object):
    def __init__(self, pyramid_alpha_to, pyramid_alpha_from, pyramid_alpha_time, stones_plate, stones,
                 stone_anchor_shift_on_magnet, mobile_positions_movie_name):
        self.pyramid_alpha_to = pyramid_alpha_to
        self.pyramid_alpha_from = pyramid_alpha_from
        self.pyramid_alpha_time = pyramid_alpha_time

        self.stones_plate = stones_plate
        self.stones = stones

        self.stone_anchor_shift_on_magnet = stone_anchor_shift_on_magnet
        self.mobile_positions_movie_name = mobile_positions_movie_name


class StonePyramidsManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	StonesPlate	PyramidAlphaTo	PyramidAlphaFrom	PyramidAlphaTime	StonesParamXlsx 
            [StoneAnchorShiftOnMagnet]
            '''
            enigma_name = record.get('EnigmaName')
            pyramid_alpha_to = record.get('PyramidAlphaTo')
            pyramid_alpha_from = record.get('PyramidAlphaFrom')
            pyramid_alpha_time = record.get('PyramidAlphaTime')
            stones_plate = record.get('StonesPlate')
            stones_param_xlsx = record.get('StonesParamXlsx')
            stone_anchor_shift_on_magnet = tuple(record.get('StoneAnchorShiftOnMagnet', [0.0, 40.0]))
            mobile_positions_movie_name = record.get('MobilePositionsMovieName', "Movie2_MobilePositions")

            result = StonePyramidsManager.addParam(enigma_name, module, pyramid_alpha_to, pyramid_alpha_from,
                                                   pyramid_alpha_time, stones_plate, stones_param_xlsx,
                                                   stone_anchor_shift_on_magnet, mobile_positions_movie_name)

            if result is False:
                error_msg = "StonePyramidsManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, pyramid_alpha_to, pyramid_alpha_from, pyramid_alpha_time, stones_plate,
                 stones_param_xlsx, stone_anchor_shift_on_magnet, mobile_positions_movie_name):
        if enigma_name in StonePyramidsManager.s_params:
            error_msg = "StonePyramidsManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        stones = dict()
        if stones_param_xlsx is not None:
            records = DatabaseManager.getDatabaseRecords(module, stones_param_xlsx)
            if records is None:
                error_msg = "StonePyramidsManager cant find MissMoviesXlsx database for {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

            for record in records:
                '''
                Start	Select	Finish	Fall	SlotTo
                '''
                stone_param = dict()
                slot_to = record.get('SlotTo')

                stone_param['Start'] = record.get('Start')
                stone_param['Select'] = record.get('Select')
                stone_param['Finish'] = record.get('Finish')
                stone_param['Fall'] = record.get('Fall')
                stone_param['SlotTo'] = slot_to

                stones[slot_to] = stone_param

        param = StonePyramidsParam(pyramid_alpha_to, pyramid_alpha_from, pyramid_alpha_time, stones_plate, stones,
                                   stone_anchor_shift_on_magnet, mobile_positions_movie_name)
        StonePyramidsManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return StonePyramidsManager.s_params.get(enigma_name)
