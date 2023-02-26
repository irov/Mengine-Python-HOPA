from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class DrawMagicSymbolParam(object):
    def __init__(self, symbols, symbols_complete, symbols_fail, boundary, all_symbols_complete, cursor, draw_all_at_once, auto_draw_animation_speed, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, drop_progress_on_symbol_draw_fail, use_background_timer_game_rule, background_timer_movie_name, background_win_movie_name, background_fail_movie_name, background_timer_scale, background_movie_change_alpha_time):
        """
        order matter, so we use list here:

        self.symbols = [
            [symbol_name_0, [socket_path_0, ... ,socket_path_n]],
            ...
            [symbol_name_n, [socket_path_0, ... ,socket_path_n]]
        ]

        """
        self.symbols = symbols
        self.symbols_complete = symbols_complete
        self.symbols_fail = symbols_fail
        self.boundary = boundary
        self.all_symbols_complete = all_symbols_complete
        self.cursor = cursor
        self.draw_all_at_once = draw_all_at_once
        self.auto_draw_animation_speed = auto_draw_animation_speed

        self.cursor_movie_alpha_time = cursor_movie_alpha_appear_time
        self.hide_cursor = hide_cursor
        self.symbol_movie_alpha_time = symbol_movie_alpha_time

        self.drop_progress_on_symbol_draw_fail = drop_progress_on_symbol_draw_fail

        self.use_background_timer_game_rule = use_background_timer_game_rule
        self.background_timer_movie_name = background_timer_movie_name
        self.background_win_movie_name = background_win_movie_name
        self.background_fail_movie_name = background_fail_movie_name
        self.background_timer_scale = background_timer_scale
        self.background_movie_change_alpha_time = background_movie_change_alpha_time

class DrawMagicSymbolsManager(Manager):
    s_draw_magic_symbol_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName  SymbolParam SymbolPathParam 
            BoundarySocketMovie2Name AllSymbolsCompleteMovie2Name CursorMovie2Name
            SymbolsAppearAllAtOnce AutoDrawAnimationSpeed
            
            CursorMovieAlphaAppearTime	HideCursor	SymbolMovieAlphaTime
            
            DropProgressOnSymbolDrawFail
            
            UseBackgroundTimerGameRule	BackgroundTimerMovieName	
            BackgroundWinMovieName	BackgroundFailMovieName	
            BackgroundTimerScale	BackgroundMovieChangeAlphaTime
            '''
            enigma_name = record.get('EnigmaName')
            symbol_param = record.get('SymbolParam')
            symbol_path_param = record.get('SymbolPathParam')
            boundary_name = record.get('BoundarySocketMovie2Name')
            all_symbols_complete_name = record.get('AllSymbolsCompleteMovie2Name')
            cursor_movie_name = record.get('CursorMovie2Name')

            symbol_appear_all_at_once = bool(record.get('SymbolsAppearAllAtOnce', False))
            auto_draw_animation_speed = int(record.get('AutoDrawAnimationSpeed', 3))

            cursor_movie_alpha_appear_time = float(record.get('CursorMovieAlphaAppearTime', 500.0))
            hide_cursor = bool(record.get('HideCursor', False))
            symbol_movie_alpha_time = float(record.get('SymbolMovieAlphaTime', 640.0))

            drop_progress_on_symbol_draw_fail = bool(record.get('DropProgressOnSymbolDrawFail', False))

            use_background_timer_game_rule = bool(record.get('UseBackgroundTimerGameRule', False))

            background_timer_movie_name = record.get('BackgroundTimerMovieName')
            background_win_movie_name = record.get('BackgroundWinMovieName')
            background_fail_movie_name = record.get('BackgroundFailMovieName')

            background_timer_scale = float(record.get('BackgroundTimerScale', 1.0))
            background_movie_change_alpha_time = float(record.get('BackgroundMovieChangeAlphaTime', 100.0))

            result = DrawMagicSymbolsManager.addParam(enigma_name, module, symbol_param, symbol_path_param, boundary_name, all_symbols_complete_name, cursor_movie_name, symbol_appear_all_at_once, auto_draw_animation_speed, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, drop_progress_on_symbol_draw_fail, use_background_timer_game_rule, background_timer_movie_name, background_win_movie_name, background_fail_movie_name, background_timer_scale, background_movie_change_alpha_time)
            if result is False:
                error_msg = "DrawMagicSymbolsManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, symbol_param, symbol_path_param, boundary_name, all_symbols_complete_name, cursor_movie_name, symbol_appear_all_at_once, auto_draw_animation_speed, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, drop_progress_on_symbol_draw_fail, use_background_timer_game_rule, background_timer_movie_name, background_win_movie_name, background_fail_movie_name, background_timer_scale, background_movie_change_alpha_time):
        symbols = list()
        symbols_complete = dict()
        symbols_fail = dict()

        if enigma_name in DrawMagicSymbolsManager.s_draw_magic_symbol_params:
            error_msg = "DrawMagicSymbolsManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        ''' Validate Background Timer Rule feature '''
        if use_background_timer_game_rule:
            if background_win_movie_name is None or background_fail_movie_name is None or background_timer_movie_name is None:
                error_msg = "DrawMagicSymbolsManager param UseBackgroundTimerGameRule in Enigma: \"%s\" is True. " \
                            "So background movies names shouldn't be None!" % enigma_name

                Trace.log("Manager", 0, error_msg)

                return False

        records = DatabaseManager.getDatabaseRecords(module, symbol_param)
        if records is None:
            error_msg = "DrawMagicSymbolsManager cant find SymbolPathParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        symbols = [[str(), []] for i in range(len(records))]  # for proper work of list.insert()
        for record in records:
            '''
            SymbolMovie2Name  SymbolCompleteMovie2Name  SymbolFailMovie2Name SymbolOrderIndex
            '''
            symbol_name = record.get('SymbolMovie2Name')
            symbol_complete_name = record.get('SymbolCompleteMovie2Name')
            symbol_fail_name = record.get('SymbolFailMovie2Name')
            symbol_index = record.get('SymbolOrderIndex')

            symbols[symbol_index][0] = symbol_name
            symbols_complete[symbol_name] = symbol_complete_name
            symbols_fail[symbol_name] = symbol_fail_name

        records = DatabaseManager.getDatabaseRecords(module, symbol_path_param)
        if records is None:
            error_msg = "DrawMagicSymbolsManager cant find SymbolParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            SymbolMovie2Name	SymbolPathSocketName	SymbolPathSocketOrderIndex
            '''
            symbol_name = record.get('SymbolMovie2Name')
            socket_name = record.get('SymbolPathSocketName')
            socket_index = record.get('SymbolPathSocketOrderIndex')

            for symbol_path_pair in symbols:
                if symbol_path_pair[0] == symbol_name:
                    symbol_path_pair[1].append((socket_index, socket_name))

        for symbol_name, symbol_path_list in symbols:
            symbol_path_list.sort()
            for socket_index, socket_name in symbol_path_list:
                symbol_path_list[socket_index] = socket_name

        param = DrawMagicSymbolParam(symbols, symbols_complete, symbols_fail, boundary_name, all_symbols_complete_name, cursor_movie_name, symbol_appear_all_at_once, auto_draw_animation_speed, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, drop_progress_on_symbol_draw_fail, use_background_timer_game_rule, background_timer_movie_name, background_win_movie_name, background_fail_movie_name, background_timer_scale, background_movie_change_alpha_time)

        DrawMagicSymbolsManager.s_draw_magic_symbol_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return DrawMagicSymbolsManager.s_draw_magic_symbol_params.get(enigma_name)