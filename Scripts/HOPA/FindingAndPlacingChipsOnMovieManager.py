from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class FindingAndPlacingChipsOnMovieManager(Manager):
    s_puzzles = {}

    class ChipParam(object):
        def __init__(self, chip_id, chip_movie_name, movie_place_name, place_slot):
            self.chip_id = chip_id
            self.chip_movie_name = chip_movie_name
            self.movie_place_name = movie_place_name
            self.place_slot = place_slot

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName	Param
            '''
            enigma_name = record.get('EnigmaName')
            param = record.get('Param')
            result = FindingAndPlacingChipsOnMovieManager.addParam(enigma_name, module, param)

            if result is False:
                error_message = "FindingAndPlacingChipsOnMovieManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_message)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, param):
        if enigma_name in FindingAndPlacingChipsOnMovieManager.s_puzzles:
            error_msg = "FindingAndPlacingChipsOnMovieManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        params_dict = {}
        records = DatabaseManager.getDatabaseRecords(module, param)

        if records is None:
            error_msg = "FindingAndPlacingChipsOnMovieManager cant find params database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	ChipMovieName	PlaceMovieName  PlaceSlot
            '''
            chip_id = record.get('ChipID')
            chip_movie_name = record.get('ChipMovieName')
            place_movie_name = record.get('PlaceMovieName')
            place_slot = record.get('PlaceSlot')

            params_dict[chip_id] = FindingAndPlacingChipsOnMovieManager.ChipParam(chip_id, chip_movie_name, place_movie_name, place_slot)

        FindingAndPlacingChipsOnMovieManager.s_puzzles[enigma_name] = params_dict

    @staticmethod
    def getParams(enigma_name):
        return FindingAndPlacingChipsOnMovieManager.s_puzzles.get(enigma_name)