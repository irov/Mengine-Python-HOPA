# coding=utf-8
from Event import Event
from Foundation.TaskManager import TaskManager
from HOPA.CursorMaskFindInvisibleChipManager import CursorMaskFindInvisibleChipManager
from Holder import Holder


Enigma = Mengine.importEntity("Enigma")


class SymbolHint(object):
    IDLE_STATE = 'idle'
    SELECT_STATE = 'select'
    FAIL_STATE = 'fail'

    STATE_CHANGE_ALPHA_TIME = -1

    def __init__(self, index, movie_idle, movie_select, movie_fail):
        movie_idle.setEnable(True)
        movie_idle.setPlay(True)
        movie_idle.setLoop(True)

        movie_select.setEnable(False)
        movie_fail.setEnable(False)

        self.index = index
        self.movies = {
            SymbolHint.IDLE_STATE: movie_idle,
            SymbolHint.SELECT_STATE: movie_select,
            SymbolHint.FAIL_STATE: movie_fail
        }

        self.cur_movie = movie_idle

    def scopeChangeCurState(self, source, state):
        movie = self.movies[state]

        if SymbolHint.STATE_CHANGE_ALPHA_TIME != -1:
            source.addTask("TaskNodeAlphaTo", Node=self.cur_movie.getEntityNode(), From=1.0, To=0.0,
                           Time=SymbolHint.STATE_CHANGE_ALPHA_TIME)
        source.addDisable(self.cur_movie)

        source.addEnable(movie)
        if SymbolHint.STATE_CHANGE_ALPHA_TIME != -1:
            source.addTask("TaskNodeAlphaTo", Node=movie.getEntityNode(), From=0.0, To=1.0,
                           Time=SymbolHint.STATE_CHANGE_ALPHA_TIME)

        self.cur_movie = movie

    def scopePlayCurMovie(self, source, **params):
        source.addPlay(self.cur_movie, **params)


class Symbol(object):
    """
    IDLE_ANIM_MODE:
        0 – always play loop;
        1 – play once on appear;
        2 – play on cursor click;
        3 – play on cursor enter.

    SELECT_ANIM_MODE:
        0 – always play loop;
        1 – play once on appear;
        2 – play on cursor click;
        3 – play on cursor enter.

    """
    IDLE_STATE = 'idle'
    SELECT_STATE = 'select'
    FAIL_STATE = 'fail'

    IDLE_ANIM_MODE = 2
    SELECT_ANIM_MODE = 0
    STATE_CHANGE_ALPHA_TIME = -1

    EVENT_MOVIE_ENABLE = None

    def __init__(self, index, movie_idle, movie_select, movie_fail, symbol_hint):
        """
        """

        '''
        for anim modes [0-1]
        '''
        movie_idle.setEnable(True)
        movie_idle.setPlay(Symbol.IDLE_ANIM_MODE < 2)
        movie_idle.setLoop(Symbol.IDLE_ANIM_MODE == 0)

        movie_select.setEnable(False)
        movie_select.setPlay(Symbol.SELECT_ANIM_MODE < 2)
        movie_select.setLoop(Symbol.SELECT_ANIM_MODE == 0)

        movie_fail.setEnable(False)

        self.index = index
        self.movies = {Symbol.IDLE_STATE: movie_idle, Symbol.SELECT_STATE: movie_select, Symbol.FAIL_STATE: movie_fail}
        self.symbol_hint = symbol_hint

        self.cur_movie = movie_idle
        self.found = False

        self.__tc_play = None

    def setCurMovie(self, movie):
        self.cur_movie = movie

    def scopeIdleMovieClick(self, source, blockSourceIfFound=False, waitToEnableIfDisabled=False):
        if blockSourceIfFound and self.found:
            source.addBlock()
            return

        movie = self.movies[Symbol.IDLE_STATE]

        if not movie.getEnable():
            if waitToEnableIfDisabled:
                source.addEvent(Symbol.EVENT_MOVIE_ENABLE,
                                lambda symbol, symbol_movie: symbol is self and symbol_movie is movie)
            else:
                source.addBlock()
                return

        source.addTask("TaskMovie2SocketClick", Movie2=movie, SocketName='socket')

    def scopeChangeCurState(self, source, state):
        prev_movie = self.cur_movie
        movie = self.movies[state]
        self.found = movie is self.movies[Symbol.SELECT_STATE]

        if SymbolHint.STATE_CHANGE_ALPHA_TIME != -1:
            source.addTask("TaskNodeAlphaTo", Node=prev_movie.getEntityNode(), From=1.0, To=0.0,
                           Time=Symbol.STATE_CHANGE_ALPHA_TIME)

        source.addEnable(movie)
        source.addFunction(self.setCurMovie, movie)
        source.addFunction(Symbol.EVENT_MOVIE_ENABLE, self, movie)

        source.addDisable(prev_movie)

        if SymbolHint.STATE_CHANGE_ALPHA_TIME != -1:
            source.addTask("TaskNodeAlphaTo", Node=movie.getEntityNode(), From=0.0, To=1.0,
                           Time=Symbol.STATE_CHANGE_ALPHA_TIME)

    def scopePlayCurMovie(self, source, **params):
        source.addPlay(self.cur_movie, **params)

    def enablePlayTC(self):
        """
        for anim modes [2-3]
        """
        if Symbol.IDLE_ANIM_MODE < 2 and Symbol.SELECT_ANIM_MODE < 2:
            return

        self.__tc_play = TaskManager.createTaskChain(Repeat=True)

        def __switch(is_skip, cb):
            """
            0 - no play condition listen event movie enable
            # 1 - play 'idle' movie on cursor click // disabled, moved to: symbols SymbolHintsManager->scopeValidClick
            2 - play 'idle' movie on cursor enter
            3 - play 'select' movie on cursor click
            4 - play 'select' movie on cursor enter
            """

            switch = 0
            if self.cur_movie is self.movies[Symbol.IDLE_STATE]:
                if Symbol.IDLE_ANIM_MODE == 3:
                    switch = 2  # elif Symbol.IDLE_ANIM_MODE == 2:  #     switch = 1
            elif self.cur_movie is self.movies[Symbol.SELECT_STATE]:
                if Symbol.SELECT_ANIM_MODE == 2:
                    switch = 3
                elif Symbol.SELECT_ANIM_MODE == 3:
                    switch = 4

            cb(is_skip, switch)

        with self.__tc_play as tc:
            with tc.addRaceTask(2) as (race_0, race_1):
                race_0.addEvent(Symbol.EVENT_MOVIE_ENABLE,
                                lambda symbol, movie: symbol is self and movie is not self.movies[Symbol.FAIL_STATE])

                with race_1.addSwitchTask(5, __switch) as (wait_0, play_1, play_2, play_3, play_4):
                    wait_0.addEvent(Symbol.EVENT_MOVIE_ENABLE,
                                    lambda symbol, movie: symbol is self and movie is not self.movies[Symbol.FAIL_STATE])

                    play_1.addTask("TaskMovie2SocketClick", Movie2=self.movies[Symbol.IDLE_STATE], SocketName='socket')
                    play_1.addTask("TaskMovie2Play", Movie2=self.movies[Symbol.IDLE_STATE], Wait=True)

                    play_2.addTask("TaskMovie2SocketEnter", Movie2=self.movies[Symbol.IDLE_STATE], SocketName='socket')
                    play_2.addTask("TaskMovie2Play", Movie2=self.movies[Symbol.IDLE_STATE], Wait=True)

                    play_3.addTask("TaskMovie2SocketClick", Movie2=self.movies[Symbol.SELECT_STATE], SocketName='socket')
                    play_3.addTask("TaskMovie2Play", Movie2=self.movies[Symbol.SELECT_STATE], Wait=True)

                    play_4.addTask("TaskMovie2SocketEnter", Movie2=self.movies[Symbol.SELECT_STATE], SocketName='socket')
                    play_4.addTask("TaskMovie2Play", Movie2=self.movies[Symbol.SELECT_STATE], Wait=True)

    def disablePlayTC(self):
        if self.__tc_play is not None:
            self.__tc_play.cancel()

    def cleanUp(self):
        self.disablePlayTC()


class SymbolHintsManager(object):
    """
    SYMBOL_HINT_PLAY_ON_FAIL_MODE:
        0 – play fail current hint;
        1 – play fail for all hints;
    """

    SYMBOL_HINT_PLAY_ON_FAIL_MODE = 1
    EVENT_EMPTY_HINT_QUEUE = None

    def __init__(self, symbols, symbol_hints):
        self.symbols = symbols
        self.symbol_hints_queue = symbol_hints
        self.symbol_holder = Holder()

    def enableSymbolsPlayTC(self, enable):
        if enable:
            for symbol in self.symbols:
                symbol.enablePlayTC()
        else:
            for symbol in self.symbols:
                symbol.disablePlayTC()

    def scopeValidClick(self, source):
        symbol = self.symbol_holder.get()
        symbol_hint = self.symbol_hints_queue.pop(0)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            if symbol.IDLE_ANIM_MODE == 2:
                parallel_0.addScope(symbol.scopePlayCurMovie, Wait=True)
            parallel_0.addScope(symbol.scopeChangeCurState, symbol.SELECT_STATE)

            parallel_1.addScope(symbol_hint.scopeChangeCurState, symbol_hint.SELECT_STATE)
            parallel_1.addScope(symbol_hint.scopePlayCurMovie, Wait=False)

        if len(self.symbol_hints_queue) == 0:
            source.addFunction(SymbolHintsManager.EVENT_EMPTY_HINT_QUEUE)

    def scopeInvalidClick(self, source):
        symbol = self.symbol_holder.get()
        fail_play_objects = list()

        if SymbolHintsManager.SYMBOL_HINT_PLAY_ON_FAIL_MODE == 0:
            fail_play_objects = [symbol, self.symbol_hints_queue[0]]

        elif SymbolHintsManager.SYMBOL_HINT_PLAY_ON_FAIL_MODE == 1:
            fail_play_objects = list(self.symbol_hints_queue)
            fail_play_objects.append(symbol)

        for fail_play_object, parallel in source.addParallelTaskList(fail_play_objects):
            parallel.addScope(fail_play_object.scopeChangeCurState, fail_play_object.FAIL_STATE)
            parallel.addScope(fail_play_object.scopePlayCurMovie, Wait=True)
            parallel.addScope(fail_play_object.scopeChangeCurState, fail_play_object.IDLE_STATE)

    def scopeResolveSymbolIdleClick(self, source):
        for symbol, race in source.addRaceTaskList(self.symbols):
            race.addScope(symbol.scopeIdleMovieClick, blockSourceIfFound=True, waitToEnableIfDisabled=True)
            race.addFunction(self.symbol_holder.set, symbol)

        with source.addIfTask(lambda: self.symbol_holder.get().symbol_hint is self.symbol_hints_queue[0]) as (true, false):
            true.addScope(self.scopeValidClick)
            false.addScope(self.scopeInvalidClick)

    @staticmethod
    def scopeComplete(source):
        source.addEvent(SymbolHintsManager.EVENT_EMPTY_HINT_QUEUE)

    def cleanUp(self):
        for symbol in self.symbols:
            symbol.cleanUp()


class CursorMaskFindInvisibleChip(Enigma):
    def __init__(self):
        super(CursorMaskFindInvisibleChip, self).__init__()
        self.tc_main = None

        self.params = None

        self.symbol_hints_manager = None

        self.cursor_movie_with_mask = None
        self.tc_move_cursor_movie_with_mask = None

        self.tc_smooth_alpha_cursor = None
        self.tc_smooth_alpha_cursor_movie_with_mask = None

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def loadParam(self):
        self.params = CursorMaskFindInvisibleChipManager.getParam(self.EnigmaName)

    def setup(self):
        """
        """
        get_movie = self.object.getObject
        self.cursor_movie_with_mask = get_movie(self.params.movie2_cursor)
        self.cursor_movie_with_mask.setEnable(True)
        self.cursor_movie_with_mask.setAlpha(0.0)

        '''
        setup Symbol, SymbolHint, SymbolHintManager class attributes
        '''
        SymbolHint.STATE_CHANGE_ALPHA_TIME = self.params.hint_state_change_alpha_time

        Symbol.IDLE_ANIM_MODE = self.params.symbol_idle_anim_mode
        Symbol.SELECT_ANIM_MODE = self.params.symbol_select_anim_mode
        Symbol.STATE_CHANGE_ALPHA_TIME = self.params.symbol_state_change_alpha_time

        Symbol.EVENT_MOVIE_ENABLE = Event('Event{}SymbolMovieEnable'.format(self.EnigmaName))

        SymbolHintsManager.SYMBOL_HINT_PLAY_ON_FAIL_MODE = self.params.hint_symbol_play_on_fail_mode
        SymbolHintsManager.EVENT_EMPTY_HINT_QUEUE = Event('Event{}EmptyHintQueue'.format(self.EnigmaName))

        '''
        create Symbols and Symbol_Hints objects
        '''
        symbols = list()
        symbol_hints = list()

        for index, symbols_param_list in self.params.symbols.items():
            for (movie2_hint_idle_name, movie2_hint_select_name, movie2_hint_fail_name, movie2_symbol_idle_name,
                 movie2_symbol_select_name, movie2_symbol_fail_name) in symbols_param_list:
                movie2_symbol_idle = get_movie(movie2_symbol_idle_name)
                movie2_symbol_select = get_movie(movie2_symbol_select_name)
                movie2_symbol_fail = get_movie(movie2_symbol_fail_name)

                symbol_hint = None
                if index != -1:
                    movie2_hint_idle = get_movie(movie2_hint_idle_name)
                    movie2_hint_select = get_movie(movie2_hint_select_name)
                    movie2_hint_fail = get_movie(movie2_hint_fail_name)

                    symbol_hint = SymbolHint(index, movie2_hint_idle, movie2_hint_select, movie2_hint_fail)
                    symbol_hints.append(symbol_hint)

                symbol = Symbol(index, movie2_symbol_idle, movie2_symbol_select, movie2_symbol_fail, symbol_hint)
                symbols.append(symbol)

        '''
        create SymbolHintManager
        '''
        symbols.sort(key=lambda obj: obj.index)
        symbol_hints.sort(key=lambda obj: obj.index)

        self.symbol_hints_manager = SymbolHintsManager(symbols, symbol_hints)

    def cleanUp(self):
        if self.tc_main is not None:
            self.tc_main.cancel()
            self.tc_main = None

        if self.tc_move_cursor_movie_with_mask is not None:
            self.tc_move_cursor_movie_with_mask.cancel()
            self.tc_move_cursor_movie_with_mask = None

        if SymbolHintsManager is not None:
            self.symbol_hints_manager.cleanUp()
            self.symbol_hints_manager = None

        if not self.params.cursor_enable_bool:
            self.setCursorSmoothAlpha(1.0)

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def setCursorSmoothAlpha(self, alpha_to):
        arrow_node = Mengine.getArrow().node

        if self.params.cursor_movie_alpha_time == -1:
            arrow_node.getRender().setLocalAlpha(alpha_to)

        else:
            if self.tc_smooth_alpha_cursor is not None:
                self.tc_smooth_alpha_cursor.cancel()

            self.tc_smooth_alpha_cursor = TaskManager.createTaskChain(Repeat=False)

            with self.tc_smooth_alpha_cursor as tc:
                tc.addTask("TaskNodeAlphaTo", Node=arrow_node, To=alpha_to, Time=self.params.cursor_movie_alpha_time)

    def setCursorMovieSmoothAlpha(self, alpha_to):
        if self.params.cursor_movie_alpha_time == -1:
            self.cursor_movie_with_mask.setAlpha(alpha_to)

        else:
            if self.tc_smooth_alpha_cursor_movie_with_mask is not None:
                self.tc_smooth_alpha_cursor_movie_with_mask.cancel()

            self.tc_smooth_alpha_cursor_movie_with_mask = TaskManager.createTaskChain(Repeat=False)

            with self.tc_smooth_alpha_cursor_movie_with_mask as tc:
                tc.addTask("TaskNodeAlphaTo", Node=self.cursor_movie_with_mask.getEntityNode(), To=alpha_to,
                           Time=self.params.cursor_movie_alpha_time)

    def enableMoveCursorMovieTC(self, enable):
        if enable:
            if self.tc_move_cursor_movie_with_mask is not None:
                self.tc_move_cursor_movie_with_mask.cancel()

            self.tc_move_cursor_movie_with_mask = TaskManager.createTaskChain(Repeat=True)

            cursor_movie_with_mask_en = self.cursor_movie_with_mask.getEntityNode()

            def __tracker(_touchId, x, y, _dx, _dy):
                cursor_movie_with_mask_en.setLocalPosition((x, y))

            with self.tc_move_cursor_movie_with_mask as tc:
                tc.addTask("TaskMouseMove", Tracker=__tracker)

        else:
            self.tc_move_cursor_movie_with_mask.cancel()
            self.tc_move_cursor_movie_with_mask = None

    def runTaskChains(self):
        self.tc_main = TaskManager.createTaskChain(Repeat=False)

        with self.tc_main as tc:
            tc.addFunction(self.enableMoveCursorMovieTC, True)

            tc.addFunction(self.setCursorMovieSmoothAlpha, 1.0)

            if not self.params.cursor_enable_bool:
                tc.addFunction(self.setCursorSmoothAlpha, 0.0)

            tc.addFunction(self.symbol_hints_manager.enableSymbolsPlayTC, True)

            with tc.addRepeatTask() as (repeat, until):
                repeat.addScope(self.symbol_hints_manager.scopeResolveSymbolIdleClick)
                until.addScope(self.symbol_hints_manager.scopeComplete)

            tc.addFunction(self.enableMoveCursorMovieTC, False)

            tc.addFunction(self.setCursorMovieSmoothAlpha, 1.0)

            if not self.params.cursor_enable_bool:
                tc.addFunction(self.setCursorSmoothAlpha, 1.0)

            tc.addFunction(self.enigmaComplete)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(CursorMaskFindInvisibleChip, self)._onPreparation()
        self.loadParam()
        self.setup()

    def _onActivate(self):
        super(CursorMaskFindInvisibleChip, self)._onActivate()

    def _onDeactivate(self):
        super(CursorMaskFindInvisibleChip, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.runTaskChains()

    def _stopEnigma(self):
        if self.tc_main is not None:
            self.tc_main.cancel()

    def _restoreEnigma(self):
        self.runTaskChains()

    def _resetEnigma(self):
        self.cleanUp()
        self.setup()
        self.runTaskChains()

    def _skipEnigma(self):
        return
