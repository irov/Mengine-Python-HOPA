from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class CursorMaskFindInvisibleChipParam(object):
    def __init__(self, symbols, cursor_enable_bool, cursor_movie_alpha_time, symbol_idle_anim_mode, symbol_select_anim_mode, hint_state_change_alpha_time, symbol_state_change_alpha_time, hint_symbol_play_on_fail_mode, movie2_cursor):
        self.movie2_cursor = movie2_cursor

        self.symbols = symbols

        self.cursor_enable_bool = cursor_enable_bool
        self.cursor_movie_alpha_time = cursor_movie_alpha_time
        self.hint_symbol_play_on_fail_mode = hint_symbol_play_on_fail_mode

        self.symbol_idle_anim_mode = symbol_idle_anim_mode
        self.symbol_select_anim_mode = symbol_select_anim_mode

        self.hint_state_change_alpha_time = hint_state_change_alpha_time
        self.symbol_state_change_alpha_time = symbol_state_change_alpha_time

class CursorMaskFindInvisibleChipManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	CursorEnableBool	CursorMovieAlphaTime	HintStateChangeAlphaTime	
            SymbolStateChangeAlphaTime	SymbolIdleAnimMode	SymbolSelectAnimMode	
            HintSymbolPlayOnFailMode	Movie2_Cursor	SymbolParamXlsx
            '''
            enigma_name = record.get('EnigmaName')
            cursor_enable_bool = bool(record.get('CursorEnableBool'))
            cursor_movie_alpha_time = record.get('CursorMovieAlphaTime')
            symbol_idle_anim_mode = record.get('SymbolIdleAnimMode')
            symbol_select_anim_mode = record.get('SymbolSelectAnimMode')
            hint_state_change_alpha_time = record.get('HintStateChangeAlphaTime')
            symbol_state_change_alpha_time = record.get('SymbolStateChangeAlphaTime')
            hint_symbol_play_on_fail_mode = record.get('HintSymbolPlayOnFailMode')
            movie2_cursor = record.get('Movie2_Cursor')
            symbol_param_xlsx = record.get('SymbolParamXlsx')

            result = CursorMaskFindInvisibleChipManager.addParam(enigma_name, module, cursor_enable_bool, cursor_movie_alpha_time, symbol_idle_anim_mode, symbol_select_anim_mode, hint_state_change_alpha_time, symbol_state_change_alpha_time, hint_symbol_play_on_fail_mode, movie2_cursor, symbol_param_xlsx)

            if result is False:
                error_msg = "CursorMaskFindInvisibleChipManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, cursor_enable_bool, cursor_movie_alpha_time, symbol_idle_anim_mode, symbol_select_anim_mode, hint_state_change_alpha_time, symbol_state_change_alpha_time, hint_symbol_play_on_fail_mode, movie2_cursor, symbol_param_xlsx):
        if enigma_name in CursorMaskFindInvisibleChipManager.s_params:
            error_msg = "CursorMaskFindInvisibleChipManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, symbol_param_xlsx)
        if records is None:
            error_msg = "CursorMaskFindInvisibleChipManager cant find symbol_param_xlsx database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        symbols = dict()
        for record in records:
            '''
            Index	Movie2_HintIdle	Movie2_HintSelect	Movie2_HintFail	Movie2_SymbolIdle	Movie2_SymbolSelect	
            Movie2_SymbolFail
            '''
            index = record.get('Index')

            movie2_hint_idle = record.get('Movie2_HintIdle')
            movie2_hint_select = record.get('Movie2_HintSelect')
            movie2_hint_fail = record.get('Movie2_HintFail')
            movie2_symbol_idle = record.get('Movie2_SymbolIdle')
            movie2_symbol_select = record.get('Movie2_SymbolSelect')
            movie2_symbol_fail = record.get('Movie2_SymbolFail')

            if index not in symbols:
                symbols[index] = []

            symbols[index].append((movie2_hint_idle, movie2_hint_select, movie2_hint_fail, movie2_symbol_idle, movie2_symbol_select, movie2_symbol_fail))

        param = CursorMaskFindInvisibleChipParam(symbols, cursor_enable_bool, cursor_movie_alpha_time, symbol_idle_anim_mode, symbol_select_anim_mode, hint_state_change_alpha_time, symbol_state_change_alpha_time, hint_symbol_play_on_fail_mode, movie2_cursor)
        CursorMaskFindInvisibleChipManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return CursorMaskFindInvisibleChipManager.s_params.get(enigma_name)