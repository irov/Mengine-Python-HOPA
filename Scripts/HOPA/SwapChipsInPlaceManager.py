from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class SwapChipsInPlaceManager(Manager):
    s_puzzles = {}

    class SwapChipsInPlaceParam(object):
        def __init__(self, chips_dict, place_dict, rotate_dict, start_comb_dict, wins_comb_dict):
            self.Chips = chips_dict
            self.Places = place_dict
            self.Rotates = rotate_dict
            self.startComb = start_comb_dict
            self.winsComb = wins_comb_dict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	Chips   Places  StartComb	WinsComb
            '''
            enigma_name = record.get('EnigmaName')
            param_chips = record.get('Chips')
            param_slots = record.get('Places')
            param_rotates = record.get('Rotates')
            start_comb = record.get('StartComb')
            wins_comb = record.get('WinsComb')

            result = SwapChipsInPlaceManager.addParam(enigma_name, module, param_chips, param_slots, param_rotates, start_comb, wins_comb)

            if result is False:
                error_message = "SwapChipsInPlaceManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_message)
                return False

        return True

    @staticmethod
    def addParam(enigma_name, module, param_chips, param_slots, param_rotates, start_comb, wins_comb):
        if enigma_name in SwapChipsInPlaceManager.s_puzzles:
            error_msg = "SwapChipsInPlaceManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        chips_dict = {}
        records = DatabaseManager.getDatabaseRecords(module, param_chips)

        if records is None:
            error_msg = "SwapChipsInPlaceManager cant find Chips database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	MovieIdle	MovieSelected	MovieName	AllowedMove	

            '''
            chip_id = record.get('ChipID')
            movie_idle = record.get('MovieIdle')
            movie_selected = record.get('MovieSelected', None)
            movie_name = record.get('MovieName', None)
            allowed_move = bool(record.get('AllowedMove', 1))
            rotate_angle = record.get('RotateAngle', 0)
            chips_dict[chip_id] = (movie_name, movie_idle, movie_selected, allowed_move, rotate_angle)
        # ==============================================================================================================

        # -------------- Places ----------------------------------------------------------------------------------------
        place_dict = {}
        records = DatabaseManager.getDatabaseRecords(module, param_slots)

        if records is None:
            error_msg = "SwapChipsInPlaceManager cant find Places database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                PlaceID	MovieName
            '''
            place_id = record.get('PlaceID')
            movie_name = record.get('MovieName')

            place_dict[place_id] = movie_name
        # ==============================================================================================================

        # -------------- Rotates ---------------------------------------------------------------------------------------
        rotate_dict = {}

        if param_rotates is not None:
            records = DatabaseManager.getDatabaseRecords(module, param_rotates)

            if records is None:
                error_msg = "SwapChipsInPlaceManager cant find Places database for {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

            for record in records:
                '''
                    ChipID	PlaceID	RotateAngle
                '''
                chip_id = record.get('ChipID')
                place_id = record.get('PlaceID')
                rotate_angle = record.get('RotateAngle')

                rotate_dict[(chip_id, place_id)] = rotate_angle

        # -------------- Start Combination -----------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, start_comb)
        start_comb_dict = {}

        if records is None:
            error_msg = "SwapChipsInPlaceManager cant find Start Combination  database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	PlaceID
            '''
            chip_id = record.get('ChipID')
            place_id = record.get('PlaceID')

            start_comb_dict[chip_id] = place_id
        # ==============================================================================================================

        # -------------- Wins Combination ------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, wins_comb)
        wins_comb_dict = {}

        if records is None:
            error_msg = "SwapChipsInPlaceManager cant find Start Combination  database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	PlaceID
            '''
            chip_id = record.get('ChipID')
            place_id = record.get('PlaceID')

            wins_comb_dict[chip_id] = place_id
        # ==============================================================================================================

        new_param = SwapChipsInPlaceManager.SwapChipsInPlaceParam(chips_dict, place_dict, rotate_dict, start_comb_dict, wins_comb_dict)

        SwapChipsInPlaceManager.s_puzzles[enigma_name] = new_param
        return True

    @staticmethod
    def getParam(enigma_name):
        return SwapChipsInPlaceManager.s_puzzles.get(enigma_name)