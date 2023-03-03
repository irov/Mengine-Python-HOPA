from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class FindSymbolsSetsMatchingCenterParam(object):
    def __init__(self, symbols, movie_win, movie_set_complete, movie_set_fail):
        self.symbols = symbols
        self.movie_win = movie_win
        self.movie_set_complete = movie_set_complete
        self.movie_set_fail = movie_set_fail


class FindSymbolsSetsMatchingCenterManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	Movie2_Win	Movie2_SetComplete	SymbolSetsXlsx  Movie2_SetFail
            '''
            enigma_name = record.get('EnigmaName')
            movie2_win = record.get('Movie2_Win')
            movie2_set_complete = record.get('Movie2_SetComplete')
            movie2_set_fail = record.get('Movie2_SetFail')
            symbol_sets_xlsx = record.get('SymbolSetsXlsx')

            result = FindSymbolsSetsMatchingCenterManager.addParam(enigma_name, module, movie2_win, movie2_set_complete,
                                                                   movie2_set_fail, symbol_sets_xlsx)

            if result is False:
                error_msg = "FindSymbolsSetsMatchingCenterManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, movie2_win, movie2_set_complete, movie2_set_fail, symbol_sets_xlsx):
        if enigma_name in FindSymbolsSetsMatchingCenterManager.s_params:
            error_msg = "FindSymbolsSetsMatchingCenterManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, symbol_sets_xlsx)
        if records is None:
            error_msg = "FindSymbolsSetsMatchingCenterManager cant find MissMoviesXlsx database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        symbols = dict()
        for record in records:
            '''
            SetToFindOrderIndex	Movie2_Center	Movie2_SymbolIdle	Movie2_SymbolSelect
            '''
            set_to_find_order_index = record.get('SetToFindOrderIndex')
            movie2_center = record.get('Movie2_Center')
            movie2_symbol_idle = record.get('Movie2_SymbolIdle')
            movie2_symbol_select = record.get('Movie2_SymbolSelect')

            if movie2_center not in symbols:
                symbols[movie2_center] = (set_to_find_order_index, [])

            symbols[movie2_center][1].append((movie2_symbol_idle, movie2_symbol_select))

        param = FindSymbolsSetsMatchingCenterParam(symbols, movie2_win, movie2_set_complete, movie2_set_fail)
        FindSymbolsSetsMatchingCenterManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return FindSymbolsSetsMatchingCenterManager.s_params.get(enigma_name)
