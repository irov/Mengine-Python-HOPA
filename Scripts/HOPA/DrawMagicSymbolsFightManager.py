from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class DrawMagicSymbolParam(object):
    def __init__(self, symbols, symbols_complete, symbols_fail, boundary, cursor, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, draw_offset, max_draw_distance, draw_distance_stop, pen_sprite_prot, draw_sound_notifier, fFightMoviesAlphaTime, fFailMovie, fight_movies, draw_sound_delay, d_symbols_shake_fx, hp_movie_name, symbols_location_type, hp_alpha_time, rotate_pen_sprite):
        self.symbols = symbols
        self.symbols_complete = symbols_complete
        self.symbols_fail = symbols_fail
        self.boundary = boundary
        self.cursor = cursor

        self.cursor_movie_alpha_time = cursor_movie_alpha_appear_time
        self.hide_cursor = hide_cursor
        self.symbol_movie_alpha_time = symbol_movie_alpha_time

        self.draw_offset = draw_offset
        self.max_draw_distance = max_draw_distance
        self.draw_distance_stop = draw_distance_stop

        self.pen_sprite_prot = pen_sprite_prot
        self.rotate_pen_sprite = rotate_pen_sprite

        self.draw_sound_notifier = draw_sound_notifier
        self.fight_movies_alpha_time = fFightMoviesAlphaTime
        self.fail_movie = fFailMovie

        self.fight_movies = fight_movies

        self.draw_sound_delay = draw_sound_delay

        self.symbols_shake_fx = d_symbols_shake_fx
        self.hp_movie_name = hp_movie_name
        self.hp_alpha_time = hp_alpha_time
        self.symbols_location_type = symbols_location_type

class DrawMagicSymbolsFightManager(Manager):
    s_draw_magic_symbol_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	FightMovieParam  SymbolParam	SymbolPathParam	
            BoundarySocketMovie2Name	
            fSymbolMovieAlphaTime	fDrawOffset	fDrawDistanceStop   DrawSoundNotifierName
            CursorMovie2Name	fCursorMovieAlphaAppearTime	bHideCursor
            fFightMoviesAlphaTime	fFailMovie  fDrawSoundDelay
            '''

            enigma_name = record.get('EnigmaName')
            symbol_param = record.get('SymbolParam')
            symbol_path_param = record.get('SymbolPathParam')
            fight_param = record.get('FightMovieParam')

            boundary_name = record.get('BoundarySocketMovie2Name')

            symbol_movie_alpha_time = float(record.get('fSymbolMovieAlphaTime', 640.0))
            draw_offset = float(record.get('fDrawOffset', 6.0))
            max_draw_distance = record.get('DrawDistance', 3000)
            draw_distance_stop = float(record.get('fDrawDistanceStop', 100.0))
            pen_sprite_prot = record.get('SpritePenPrototypeName', 'Sprite_Pen')
            rotate_pen_sprite = bool(record.get("RotatePenSprite", False))
            draw_sound_notifier = record.get('DrawSoundNotifierName', 'DrawMagicSymbols_Draw')

            cursor_movie_name = record.get('CursorMovie2Name')
            cursor_movie_alpha_appear_time = float(record.get('fCursorMovieAlphaAppearTime', 500.0))
            hide_cursor = bool(record.get('bHideCursor', False))

            fFightMoviesAlphaTime = record.get('fFightMoviesAlphaTime', 300.0)
            fFailMovie = record.get('fFailMovie', "Movie2_Fail")

            draw_sound_delay = float(record.get('fDrawSoundDelay', 60.0))

            hp_movie_name = record.get("Movie2_HPName")
            hp_alpha_time = record.get("HPAlphaTime", 300)
            symbols_location_type = bool(record.get("SymbolLocationType"))

            result = DrawMagicSymbolsFightManager.addParam(enigma_name, module, symbol_param, fight_param, symbol_path_param, boundary_name, symbol_movie_alpha_time, draw_offset, max_draw_distance, draw_distance_stop, cursor_movie_name, cursor_movie_alpha_appear_time, hide_cursor, pen_sprite_prot, draw_sound_notifier, fFightMoviesAlphaTime, fFailMovie, draw_sound_delay, hp_movie_name, symbols_location_type, hp_alpha_time, rotate_pen_sprite)
            if result is False:
                error_msg = "DrawMagicSymbolsFightManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, symbol_param, fight_param, symbol_path_param, boundary_name, symbol_movie_alpha_time, draw_offset, max_draw_distance, draw_distance_stop, cursor_movie_name, cursor_movie_alpha_appear_time, hide_cursor, pen_sprite_prot, draw_sound_notifier, fFightMoviesAlphaTime, fFailMovie, draw_sound_delay, hp_movie_name, symbols_location_type, hp_alpha_time, rotate_pen_sprite):
        symbols = list()
        symbols_complete = dict()
        symbols_fail = dict()
        fight_movies = list()
        d_symbols_shake_fx = dict()

        if enigma_name in DrawMagicSymbolsFightManager.s_draw_magic_symbol_params:
            error_msg = "DrawMagicSymbolsFightManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, symbol_param)
        if records is None:
            error_msg = "DrawMagicSymbolsFightManager cant find SymbolPathParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        symbols = [[str(), {"MultTime": [], "OneTime": []}] for _ in range(len(records))]  # for proper work of list.insert()
        for record in records:
            '''
            SymbolMovie2Name  SymbolCompleteMovie2Name  SymbolFailMovie2Name SymbolOrderIndex   ShakeFXMoviePrototype
            '''
            symbol_name = record.get('SymbolMovie2Name')
            symbol_complete_name = record.get('SymbolCompleteMovie2Name')
            symbol_fail_name = record.get('SymbolFailMovie2Name')
            symbol_index = record.get('SymbolOrderIndex')
            symbol_shake_fx = record.get('ShakeFXMoviePrototype')

            symbols[symbol_index][0] = symbol_name
            symbols_complete[symbol_name] = symbol_complete_name
            symbols_fail[symbol_name] = symbol_fail_name
            d_symbols_shake_fx[symbol_name] = symbol_shake_fx

        records = DatabaseManager.getDatabaseRecords(module, symbol_path_param)
        if records is None:
            error_msg = "DrawMagicSymbolsFightManager cant find SymbolParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            SymbolMovie2Name	SymbolPathSocketName	CanPassedMultTime
            '''
            symbol_name = record.get('SymbolMovie2Name')
            socket_name = record.get('SymbolPathSocketName')
            socket_can_path_mult_time = bool(record.get('CanPassedMultTime', False))

            for symbol_path_pair in symbols:
                if symbol_path_pair[0] == symbol_name:
                    if socket_can_path_mult_time:
                        symbol_path_pair[1]["MultTime"].append(socket_name)
                    else:
                        symbol_path_pair[1]["OneTime"].append(socket_name)

        records = DatabaseManager.getDatabaseRecords(module, fight_param)
        if records is None:
            error_msg = "DrawMagicSymbolsFightManager cant find FightMoviesParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        ''' fight movies '''
        for record in records:
            '''
            Movie2FightName	Index
            '''
            movie_fight = record.get('Movie2FightName')
            movie_idle = record.get('Movie2IdleName')
            index = record.get('Index')
            fight_movies.append((index, movie_fight, movie_idle))

        fight_movies.sort()
        fight_movies = [(movie_fight, movie_idle) for (index, movie_fight, movie_idle) in fight_movies]
        '''  '''

        param = DrawMagicSymbolParam(symbols, symbols_complete, symbols_fail, boundary_name, cursor_movie_name, cursor_movie_alpha_appear_time, hide_cursor, symbol_movie_alpha_time, draw_offset, max_draw_distance, draw_distance_stop, pen_sprite_prot, draw_sound_notifier, fFightMoviesAlphaTime, fFailMovie, fight_movies, draw_sound_delay, d_symbols_shake_fx, hp_movie_name, symbols_location_type, hp_alpha_time, rotate_pen_sprite)

        DrawMagicSymbolsFightManager.s_draw_magic_symbol_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return DrawMagicSymbolsFightManager.s_draw_magic_symbol_params.get(enigma_name)