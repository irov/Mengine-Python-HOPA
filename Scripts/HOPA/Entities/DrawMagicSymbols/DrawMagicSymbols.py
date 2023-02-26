from Event import Event
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.DrawMagicSymbolsManager import DrawMagicSymbolsManager
from Holder import Holder
from Notification import Notification

Enigma = Mengine.importEntity("Enigma")

ENIGMA_NAME_HOLDER = Holder()

MSG_SYMBOL_MOVIE_SOCKET_404 = "Enigma DrawMagicSymbols '{}' error in create Symbol instance: not found socket {} in movie {}"

class BackgroundTimer(object):
    " Implement live background with timer == (background_animation_duration * f_timer_scale) for timer chalange in mg"

    def __init__(self, movie_timer, movie_win, movie_fail, f_timer_scale, f_background_change_alpha_time):
        """

        :param movie_timer: default background movie, which animatable duration will control game try time restriction
        :param movie_win: background movie, after win (disabled on start, force play, loop)
        :param movie_fail: background movie, after fail (disabled on start, force play)
        :param f_timer_scale: MG timer multiplier
        :param f_background_change_alpha_time: background movie alpha transtion. if <= 0 no alpha
        """
        self.movie_timer = movie_timer
        self.movie_win = movie_win
        self.movie_fail = movie_fail

        self.f_background_change_alpha_time = f_background_change_alpha_time

        self.cur_movie = movie_timer

        ''' Initialize default states and values '''
        self.movie_timer.setEnable(True)  # enable on scene start
        self.movie_timer.setPlay(True)  # ** if movie is disable, movie will start playing after enable

        if f_timer_scale > 0.0:
            self.movie_timer.setSpeedFactor(f_timer_scale)

        self.movie_win.setEnable(False)
        self.movie_fail.setEnable(False)

        self.tc_alpha_to = None
        self.onInGameMenuShow = Notification.addObserver(Notificator.onInGameMenuShow, self.togglePauseTimerOnInGameMenu)

    def togglePauseTimerOnInGameMenu(self, state):
        if state is not None:
            self.movie_timer.setParam("Pause", state)
        return False

    def setCurMovie(self, movie):
        self.cur_movie = movie

    def getTimerEndEvent(self):
        return self.movie_timer.onAnimatableEnd

    def changeMovie(self, source=None, movie=None, allow_alpha=True):
        if self.tc_alpha_to is not None:  # interrupt AlphaTo tc if exists
            self.tc_alpha_to.cancel()
            self.tc_alpha_to = None

        if movie is None:
            return

        if allow_alpha and self.f_background_change_alpha_time > 0.0:
            ''' Smooth alpha transition movie change case '''

            if source is None:  # create tc with source if no source passed
                self.tc_alpha_to = TaskManager.createTaskChain(AutoRun=False)
                source = TaskSource(self.tc_alpha_to.source)

            movie.setLastFrame(False)
            movie.setPlay(False)
            movie.setEnable(True)

            with source.addParallelTask(2) as (parallel_0, parallel_1):
                source.addTask("TaskNodeAlphaTo", Node=movie.entity.node, From=0.0, To=1.0, Time=self.f_background_change_alpha_time)

                source.addTask("TaskNodeAlphaTo", Node=self.cur_movie.entity.node, To=0.0, IsTemp=True, Time=self.f_background_change_alpha_time)

            source.addDisable(self.cur_movie)
            source.addFunction(self.setCurMovie, movie)
            source.addPlay(movie)

            if self.tc_alpha_to is not None:  # if tc with source was run task chain
                self.tc_alpha_to.run()

        else:
            ''' Default movie change case '''

            if self.cur_movie.isActive() is True:
                self.cur_movie.setEnable(False)

            movie.setLastFrame(False)
            movie.setEnable(True)
            movie.setPlay(True)

            self.cur_movie = movie

class Symbol(object):
    SYMBOL_ALPHA_TIME = 500.0

    def __init__(self, id_, movie, movie_complete, movie_fail, socket_names_path_queue):
        self.id = id_

        self.movie = movie
        self.movie_complete = movie_complete
        self.movie_fail = movie_fail

        self.complete = False  # symbol draw is complete

        ''' Params for calcuation drawing effect implemented by using setTimingProportion() on movie2 instance '''
        self.socket_areas = list()
        self.socket_areas_sum = 0.0

        '''  Setup sockets path '''
        self.s_sockets_path = list()

        for socket_name in socket_names_path_queue:
            socket_path_obj = self.movie.getSocket(socket_name)

            if socket_path_obj is None:
                msg = MSG_SYMBOL_MOVIE_SOCKET_404.format(ENIGMA_NAME_HOLDER.get(), socket_name, self.movie.getName())
                Trace.log("Entity", 0, msg)

                continue

            self.s_sockets_path.append(socket_path_obj)

        ''' Initialize default states for movies '''
        self.setMoviesDefaultStates()

    def setupSocketsArea(self):
        """ on scene activated setup params for
            calcuation drawing effect
            implemented by using setTimingProportion() on movie2 instance
        """
        socket_areas = []
        socket_areas_sum = 0.0

        for socket in self.s_sockets_path:
            polygon = socket.getPolygon()
            polygon_area = polygon.area()

            socket_areas.append(polygon_area)

            socket_areas_sum += polygon_area

        self.socket_areas = socket_areas
        self.socket_areas_sum = socket_areas_sum

    def setMoviesDefaultStates(self):
        self.movie.setInteractive(True)
        self.movie.setEnable(False)
        self.movie.setLastFrame(False)  # setup first frame
        self.movie.setPlay(False)
        self.movie.setLoop(False)

        if self.movie_complete is not None:
            self.movie_complete.setEnable(False)
            self.movie_complete.setLastFrame(False)  # setup first frame
            self.movie_complete.setPlay(False)

        if self.movie_fail is not None:
            self.movie_fail.setEnable(False)
            self.movie_fail.setLastFrame(False)  # setup first frame
            self.movie_fail.setPlay(False)

    def isComplete(self):
        return self.complete

    def setComplete(self, value):
        self.complete = value

    def getSocketsPath(self):
        return self.s_sockets_path

    def scopeComplete(self, source):
        source.addFunction(self.setComplete, True)
        source.addFunction(self.movie.setTimingProportion, 1.0)

        if self.movie_complete is None:
            return

        source.addEnable(self.movie_complete)
        source.addPlay(self.movie_complete)
        source.addDisable(self.movie_complete)

    def scopeFail(self, source):
        source.addFunction(self.movie.setTimingProportion, 0.0)

        if self.movie_fail is None:
            return

        source.addEnable(self.movie_fail)
        source.addPlay(self.movie_fail)
        source.addDisable(self.movie_fail)

    def scopeAlphaEnable(self, source):
        source.addEnable(self.movie)

        source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=0.0, To=1.0, Time=Symbol.SYMBOL_ALPHA_TIME)

    def scopeAlphaDisable(self, source):
        source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=1.0, To=0.0, Time=Symbol.SYMBOL_ALPHA_TIME)

        source.addDisable(self.movie)

class DrawMagicSymbols(Enigma):

    def __init__(self):
        super(DrawMagicSymbols, self).__init__()
        self.params = None

        self.symbols_appear_all_at_once = False  # manager param
        self.auto_draw_animation_speed = 3  # manager param

        self.all_symbols_complete_movie = None  # enigma finish movie to enable-play-disable
        self.boundary = None  # movie with boundary socket
        self.cursor_movie = None  # movie attached to cursor

        self.symbols = list()

        self.current_symbol = None
        self.current_symbol_path_queue = list()  # values from here will be popped

        self.background_timer = None  # used if param.use_background_timer_game_rule == True

        self.draw_scope_calls = 0  # counter
        self.last_movie_timing_percent = 0.0  # need for smooth draw/draw cancel
        self.symbol_sockets_area_passed = 0.0

        self.__tc_main = None
        self.__tc_draw = None
        self.__tc_smooth_alpha_cursor = None
        self.__tc_smooth_alpha_cursor_movie = None
        self.__tc_movie_cursor_movie = None

        self.main_tc_semaphore = None
        self.draw_tc_semaphore = None
        self.draw_calls_update_event = None
        self.mg_interrupt_event = None

        self.b_block_reseting = Semaphore(False, "BlockResetButton")

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParams(self):
        """

        params.symbols = [
            [symbol_name_0, [socket_path_0_name, ... ,socket_path_name]],
            ...
            [symbol_name_n, [socket_path_0_name, ... ,socket_path_name]]
        ]
        params.symbols_complete = {symbol_name: symbol_complete_name}
        params.symbols_fail = {symbol_name: symbol_fail_name}

        params.draw_all_at_once = bool()
        params.auto_draw_animation_speed = int()
        params.boundary = movie 2 name
        params.all_symbols_complete = movie 2 name
        params.cursor = movie 2 name
        """

        self.params = DrawMagicSymbolsManager.getParam(self.EnigmaName)
        self.symbols_appear_all_at_once = self.params.draw_all_at_once
        self.auto_draw_animation_speed = self.params.auto_draw_animation_speed
        Symbol.SYMBOL_ALPHA_TIME = self.params.symbol_movie_alpha_time

        ENIGMA_NAME_HOLDER.set(self.EnigmaName)

    def __setup(self):
        self_object_get_object = self.object.getObject
        self_object_has_object = self.object.hasObject

        ''' creating mg objects '''
        symbols = list()

        symbol_complete_params = self.params.symbols_complete
        symbol_fail_params = self.params.symbols_fail

        for symbol_movie_name, socket_names_path_queue in self.params.symbols:
            symbol_movie = self_object_get_object(symbol_movie_name)

            symbol_complete_movie_name = symbol_complete_params[symbol_movie_name]

            if self_object_has_object(symbol_complete_movie_name):
                symbol_complete_movie = self_object_get_object(symbol_complete_movie_name)

            else:
                symbol_complete_movie = None

            symbol_fail_movie_name = symbol_fail_params[symbol_movie_name]

            if self_object_has_object(symbol_fail_movie_name):
                symbol_fail_movie = self_object_get_object(symbol_fail_movie_name)

            else:
                symbol_fail_movie = None

            symbol = Symbol(symbol_movie_name, symbol_movie, symbol_complete_movie, symbol_fail_movie, socket_names_path_queue)

            symbols.append(symbol)

        self.symbols = symbols

        self.boundary = self_object_get_object(self.params.boundary)

        ''' initialize start up values '''
        cursor_movie_name = self.params.cursor
        if self_object_has_object(cursor_movie_name):
            self.cursor_movie = self_object_get_object(cursor_movie_name)
            self.cursor_movie.setAlpha(0.0)
            self.cursor_movie.getEntityNode().setLocalPosition(Mengine.getCursorPosition())

        all_symbols_complete_movie_name = self.params.all_symbols_complete
        if all_symbols_complete_movie_name is not None:
            self.all_symbols_complete_movie = self_object_get_object(all_symbols_complete_movie_name)
            self.all_symbols_complete_movie.setEnable(False)

        if self.symbols_appear_all_at_once is False:
            symbol = self.getNextSymbol(None)
            self.__setCurrentSymbol(symbol)

        ''' create background timer '''
        if self.params.use_background_timer_game_rule:
            self.background_timer = BackgroundTimer(self_object_get_object(self.params.background_timer_movie_name), self_object_get_object(self.params.background_win_movie_name), self_object_get_object(self.params.background_fail_movie_name), self.params.background_timer_scale, self.params.background_movie_change_alpha_time)

    def __disableTCs(self):
        if self.__tc_main is not None:
            self.__tc_main.cancel()
            self.__tc_main = None

        if self.__tc_draw is not None:
            self.__tc_draw.cancel()
            self.__tc_draw = None

        if self.__tc_smooth_alpha_cursor is not None:
            self.__tc_smooth_alpha_cursor.cancel()
            self.__tc_smooth_alpha_cursor = None

        if self.__tc_smooth_alpha_cursor_movie is not None:
            self.__tc_smooth_alpha_cursor_movie.cancel()
            self.__tc_smooth_alpha_cursor_movie = None

        if self.__tc_movie_cursor_movie is not None:
            self.__tc_movie_cursor_movie.cancel()
            self.__tc_movie_cursor_movie = None

        if self.background_timer is not None:
            if self.background_timer.tc_alpha_to is not None:  # interrupt AlphaTo tc if exists
                self.background_timer.tc_alpha_to.cancel()
                self.background_timer.tc_alpha_to = None

    def __cleanUp(self):
        self.__disableTCs()
        self.current_symbol_path_queue = []

    # -------------- Getters Setters Checkers --------------------------------------------------------------------------
    def getSymbolByID(self, symbol_id):
        for symbol in self.symbols:
            if symbol.id == symbol_id:
                return symbol

    def getSymbols(self, filter_='All'):
        symbols = self.symbols
        filtered_symbols = list()

        if filter_ is 'Completed':
            for symbol in symbols:
                if symbol.isComplete() is True:
                    filtered_symbols.append(symbol)
            return filtered_symbols

        if filter_ is 'NotCompleted':
            for symbol in symbols:
                if symbol.isComplete() is False:
                    filtered_symbols.append(symbol)
            return filtered_symbols

        return symbols

    def getNextSymbol(self, cur_symbol):
        """
        will be used only if self.symbols_appear_all_at_once = False
        """
        symbols = self.symbols

        if cur_symbol is None:
            return symbols[0]

        cur_symbol_index = symbols.index(cur_symbol)

        next_symbol_index = cur_symbol_index + 1

        if next_symbol_index == len(symbols):
            return

        return symbols[next_symbol_index]

    def getSymbolsStartPathSockets(self):
        symbols = self.getSymbols(filter_='NotCompleted')
        path_beginning_sockets = dict()

        for symbol in symbols:
            path_beginning_socket = symbol.getSocketsPath()[0]
            path_beginning_sockets[symbol.id] = path_beginning_socket

        return path_beginning_sockets

    def checkSymbolComplete(self):
        if len(self.current_symbol_path_queue) == 0:
            return True
        return False

    def checkAllSymbolsComplete(self):
        symbols = self.getSymbols('NotCompleted')

        if len(symbols) == 0:
            return True
        return False

    def __setCurrentSymbol(self, symbol):
        self.current_symbol = symbol
        self.last_movie_timing_percent = 0.0
        self.symbol_sockets_area_passed = 0.0

        if symbol is None:
            self.current_symbol_path_queue = []
        else:
            self.current_symbol_path_queue = list(symbol.getSocketsPath())  # get copy

    def __scopeSwitchNextSymbolMovie(self, source):
        """
        will be used only if self.symbols_appear_all_at_once = False
        """
        source.addScope(self.current_symbol.scopeAlphaDisable)

        next_symbol = self.getNextSymbol(self.current_symbol)
        self.__setCurrentSymbol(next_symbol)

        if next_symbol is None:
            return

        source.addScope(next_symbol.scopeAlphaEnable)
        source.addFunction(next_symbol.setupSocketsArea)

    def __incrementDrawScopeCalls(self):
        self.draw_scope_calls += 1
        self.draw_calls_update_event()

    def __decrementDrawScopeCalls(self):
        self.draw_scope_calls -= 1

    # -------------- Sounds --------------------------------------------------------------------------------------------
    def __scopeSoundDraw(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "DrawMagicSymbols_Draw")

    def __scopeSoundDrawFail(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "DrawMagicSymbols_Fail")

    def __scopeSoundDrawComplete(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "DrawMagicSymbols_Complete")

    def __scopeSoundAllDrawComplete(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "DrawMagicSymbols_AllComplete")

    # -------------- Main Actions Scopes -------------------------------------------------------------------------------
    def __scopeUnDraw(self, source):
        source.addScope(self.__scopeSoundDrawFail)
        movie = self.current_symbol.movie
        percent = self.last_movie_timing_percent
        draw_range = int(percent * 100) // self.auto_draw_animation_speed

        for _ in range(draw_range):
            percent -= 0.01 * self.auto_draw_animation_speed
            self.last_movie_timing_percent = percent
            source.addFunction(movie.setTimingProportion, percent)
            source.addDelay(0.0)

    def __scopeAutoDraw(self, skip_source):
        skip_source.addScope(self.__scopeSoundDraw)
        movie = self.current_symbol.movie
        percent = 0.0
        draw_range = 100 // self.auto_draw_animation_speed

        for _ in range(draw_range):
            percent += 0.01 * self.auto_draw_animation_speed
            skip_source.addFunction(movie.setTimingProportion, percent)
            skip_source.addDelay(0.0)

    def __scopeDrawAction(self, source):
        symbol = self.current_symbol

        source.addScope(self.__scopeSoundDraw)
        source.addFunction(self.__decrementDrawScopeCalls)
        movie = symbol.movie

        sockets_num = len(symbol.getSocketsPath())

        index = len(symbol.s_sockets_path) - len(self.current_symbol_path_queue) - 1
        area = symbol.socket_areas[index]
        area_sum = symbol.socket_areas_sum

        self.symbol_sockets_area_passed += area

        timing_delta = self.symbol_sockets_area_passed / area_sum - movie.getTimingProportion()
        draw_range = int(500 / sockets_num / self.auto_draw_animation_speed)
        draw_step = timing_delta / draw_range

        # def dbgPrint():
        #     # print '\tsocket_num {} \n' \
        #     #       '\tindex {} \n' \
        #     #       '\tarea {} \n' \
        #     #       '\tarea_sum {} \n' \
        #     #       '\tarea_passed {} \n' \
        #     #       '\ttiming_delta {}\n ' \
        #     #       '\tanim_speed {}\n' \
        #     #       '\tdraw_range {} \n' \
        #     #       '\tdraw_step {} \n' \
        #     #       '\tdraw_range * draw_step {}\n' \
        #     #       '\tlast_movie_timing_percent {}\n'.format(
        #     #     sockets_num,
        #     #     index,
        #     #     area,
        #     #     area_sum,
        #     #     self.symbol_sockets_area_passed,
        #     #     timing_delta,
        #     #     self.auto_draw_animation_speed,
        #     #     draw_range,
        #     #     draw_step,
        #     #     draw_range * draw_step,
        #     #     self.last_movie_timing_percent
        #     # )
        #
        #     print \
        #         '\tindex {} \n' \
        #         '\tarea_sum {} \n' \
        #         '\tarea_passed {} \n' \
        #         '\tlast_movie_timing_percent {}\n'.format(
        #             index,
        #             area_sum,
        #             self.symbol_sockets_area_passed,
        #             self.last_movie_timing_percent
        #         )

        for _ in range(draw_range):
            self.last_movie_timing_percent += draw_step
            # source.addFunction(dbgPrint)
            source.addFunction(movie.setTimingProportion, self.last_movie_timing_percent)
            source.addDelay(0.0)

    def __scopeDraw(self, source):
        if self.draw_scope_calls < 1:
            source.addEvent(self.draw_calls_update_event)

        source.addScope(self.__scopeDrawAction)

    def __scopeAllSymbolsComplete(self, source):
        source.addScope(self.__scopeSoundAllDrawComplete)

        if self.all_symbols_complete_movie is not None:
            source.addEnable(self.all_symbols_complete_movie)
            source.addPlay(self.all_symbols_complete_movie)
            source.addDisable(self.all_symbols_complete_movie)

        source.addFunction(self.setCursorSmoothAlpha, 1.0)
        source.addFunction(self.setCursorMovieSmoothAlpha, 0.0)
        source.addFunction(self.mg_interrupt_event)

    def __scopeSymbolComplete(self, source):
        source.addSemaphore(self.draw_tc_semaphore, To=False)  # DRAW TC CONTROL
        source.addSemaphore(self.main_tc_semaphore, To=False)  # BLOCK SKIP RACE

        source.addFunction(self.current_symbol.movie.setTimingProportion, 1.0)
        source.addScope(self.__scopeSoundDrawComplete)
        source.addScope(self.current_symbol.scopeComplete)

        if self.symbols_appear_all_at_once is False:
            source.addScope(self.__scopeSwitchNextSymbolMovie)
        else:
            source.addFunction(self.__setCurrentSymbol, None)

        with source.addIfTask(self.checkAllSymbolsComplete) as (true, _):
            true.addScope(self.__scopeAllSymbolsComplete)

    # -------------- Scopes Controllers --------------------------------------------------------------------------------
    def __scopeSymbolPathNSocketEnter(self, source):
        self.current_symbol_path_queue.pop(0)
        source.addFunction(self.__incrementDrawScopeCalls)

        if self.checkSymbolComplete() is True:
            source.addScope(self.__scopeSymbolComplete)

    def __scopeDrawSymbol(self, source):
        source.addSemaphore(self.draw_tc_semaphore, To=True)  # DRAW TC CONTROL
        self.current_symbol_path_queue.pop(0)
        source.addFunction(self.__incrementDrawScopeCalls)

        for socket_path in self.current_symbol_path_queue:
            symbol_movie = self.current_symbol.movie
            socket_path_name = socket_path.getName()

            source.addTask("TaskMovie2SocketEnter", SocketName=socket_path_name, Movie2=symbol_movie, isDown=True)
            source.addScope(self.__scopeSymbolPathNSocketEnter)

    def __scopeInterruptDraw(self, source):
        with source.addRaceTask(2) as (race_button_up, race_leave_path):
            race_button_up.addTask("TaskMovie2SocketEnter", SocketName='Boundary', Movie2=self.boundary, isDown=True)
            race_leave_path.addTask("TaskMouseButtonClick", isDown=False)

        source.addSemaphore(self.main_tc_semaphore, From=True)  # IF SYMBOL COMPLETE SCOPE RUNS, BLOCK RACE
        source.addSemaphore(self.draw_tc_semaphore, To=False)  # DRAW TC CONTROL

        source.addScope(self.__scopeUnDraw)
        source.addScope(self.current_symbol.scopeFail)

        if self.params.drop_progress_on_symbol_draw_fail:
            source.addFunction(self.mg_interrupt_event)
        else:
            if self.symbols_appear_all_at_once is False:
                source.addFunction(self.__setCurrentSymbol, self.current_symbol)
            else:
                source.addFunction(self.__setCurrentSymbol, None)

    def __scopeTaskSymbolPath0SocketClickSequential(self, source):
        symbol = self.current_symbol

        symbol_movie = symbol.movie
        socket_path_0 = symbol.getSocketsPath()[0]
        socket_path_0_name = socket_path_0.getName()

        source.addTask("TaskMovie2SocketClick", SocketName=socket_path_0_name, Movie2=symbol_movie, isDown=True)

    def __scopeTaskSymbolPath0SocketClickRace(self, source):
        symbols_path_0_sockets = self.getSymbolsStartPathSockets()

        for (symbol_id, socket_path_0), race in source.addRaceTaskList(symbols_path_0_sockets.iteritems()):
            symbol = self.getSymbolByID(symbol_id)
            symbol_movie = symbol.movie
            socket_path_0_name = socket_path_0.getName()

            race.addTask("TaskMovie2SocketClick", SocketName=socket_path_0_name, Movie2=symbol_movie, isDown=True)
            race.addFunction(self.__setCurrentSymbol, symbol)

    # -------------- Cursor scopes -------------------------------------------------------------------------------------
    def setCursorSmoothAlpha(self, alpha_to, time=None):
        if not self.params.hide_cursor:
            return

        arrow_node = Mengine.getArrow().node

        if time == -1:
            arrow_node.getRender().setLocalAlpha(alpha_to)
            return

        if time is None:
            time = self.params.cursor_movie_alpha_time

        if self.__tc_smooth_alpha_cursor is not None:
            self.__tc_smooth_alpha_cursor.cancel()

        self.__tc_smooth_alpha_cursor = TaskManager.createTaskChain(Repeat=False)

        with self.__tc_smooth_alpha_cursor as tc:
            tc.addTask("TaskNodeAlphaTo", Node=arrow_node, To=alpha_to, Time=time)

    def setCursorMovieSmoothAlpha(self, alpha_to):
        if self.cursor_movie is None:
            return

        time = self.params.cursor_movie_alpha_time

        if self.__tc_smooth_alpha_cursor_movie is not None:
            self.__tc_smooth_alpha_cursor_movie.cancel()

        self.__tc_smooth_alpha_cursor_movie = TaskManager.createTaskChain(Repeat=False)

        with self.__tc_smooth_alpha_cursor_movie as tc:
            tc.addTask("TaskNodeAlphaTo", Node=self.cursor_movie.getEntityNode(), To=alpha_to, Time=time)

    def enableMoveCursorMovieTC(self, enable):
        if self.cursor_movie is None:
            return

        if enable:
            if self.__tc_movie_cursor_movie is not None:
                self.__tc_movie_cursor_movie.cancel()

            self.__tc_movie_cursor_movie = TaskManager.createTaskChain(Repeat=True)

            cursor_movie_en = self.cursor_movie.getEntityNode()

            cursor_movie_en.setLocalPosition(Mengine.getCursorPosition())

            def __tracker(_touchId, x, y, _dx, _dy):
                cursor_movie_en.setLocalPosition((x, y))

            with self.__tc_movie_cursor_movie as tc:
                tc.addTask("TaskMouseMove", Tracker=__tracker)

        else:
            self.__tc_movie_cursor_movie.cancel()
            self.__tc_movie_cursor_movie = None

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def __runGameTaskChain(self):
        if self.__tc_main is not None:  # check
            self.__tc_main.cancel()

        self.__tc_main = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_main as tc:
            tc.addSemaphore(self.b_block_reseting, From=False, To=True)

            ''' Smooth Symbol Appearing '''
            if self.symbols_appear_all_at_once is False:
                tc.addScope(self.current_symbol.scopeAlphaEnable)
                tc.addFunction(self.current_symbol.setupSocketsArea)
            else:
                for symbol, parallel in tc.addParallelTaskList(self.symbols):
                    parallel.addScope(symbol.scopeAlphaEnable)
                    parallel.addFunction(symbol.setupSocketsArea)

            tc.addSemaphore(self.b_block_reseting, To=False)

            ''' Enigma Main Gameplay Loop '''
            with tc.addRepeatTask() as (repeat, until):
                repeat.addSemaphore(self.main_tc_semaphore, To=True)

                #  switch gameplay mode (symbols appear all at once, or sequential symbol appearing)
                if self.symbols_appear_all_at_once is False:
                    repeat.addScope(self.__scopeTaskSymbolPath0SocketClickSequential)
                else:
                    repeat.addScope(self.__scopeTaskSymbolPath0SocketClickRace)

                with repeat.addRaceTask(2) as (race_draw, race_interrupt):
                    race_draw.addScope(self.__scopeDrawSymbol)
                    race_interrupt.addScope(self.__scopeInterruptDraw)

                ''' Brake Main Loop On Interrupt Gameplay Events '''
                with until.addRaceTask(2) as (race_0, race_1):
                    if self.params.use_background_timer_game_rule:
                        race_0.addEvent(self.background_timer.getTimerEndEvent())
                    else:
                        race_0.addBlock()

                    race_1.addEvent(self.mg_interrupt_event)

            ''' Handle On Interrupt Gameplay Events '''
            with tc.addIfTask(self.checkAllSymbolsComplete) as (true, false):
                if self.params.use_background_timer_game_rule:
                    true.addScope(self.background_timer.changeMovie, self.background_timer.movie_win)
                true.addFunction(self.enigmaComplete)

                if self.params.use_background_timer_game_rule:
                    false.addSemaphore(self.b_block_reseting, From=False, To=True)
                    false.addScope(self.background_timer.changeMovie, self.background_timer.movie_fail)
                    false.addSemaphore(self.b_block_reseting, To=False)
                false.addNotify(Notificator.onEnigmaReset)  # false.addDelay(1000)

    def __runDrawTaskChain(self):
        if self.__tc_draw is not None:  # check
            self.__tc_draw.cancel()
            self.__tc_draw = None

        self.__tc_draw = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_draw as tc:
            ''' Visual draw effect implemented using setTimingProportion() for symbol movie2 instances '''
            tc.addSemaphore(self.draw_tc_semaphore, From=True)

            with tc.addRaceTask(2) as (race_draw, race_interrupt):
                race_draw.addScope(self.__scopeDraw)
                race_interrupt.addSemaphore(self.draw_tc_semaphore, From=False)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(DrawMagicSymbols, self)._onPreparation()
        self.main_tc_semaphore = Semaphore(False, "EnigmaDrawMagicSymbolsMainTC")
        self.draw_tc_semaphore = Semaphore(False, "EnigmaDrawMagicSymbolsDrawTC")
        self.draw_calls_update_event = Event("EnigmaDrawMagicSymbolsDrawCallUpdate")
        self.mg_interrupt_event = Event("EnigmaDrawMagicSymbolsEventInterrupt")

        self._loadParams()
        self.__setup()

    def _onActivate(self):
        super(DrawMagicSymbols, self)._onActivate()

        ''' this tc here because it's not part of mg logic but should be applied on enigma activation '''
        with TaskManager.createTaskChain() as tc:
            tc.addDelay(1)  # fix for setCursorSmoothAlpha error in case of resumeEnigma

            tc.addFunction(self.enableMoveCursorMovieTC, True)
            tc.addFunction(self.setCursorMovieSmoothAlpha, 1.0)
            tc.addFunction(self.setCursorSmoothAlpha, 0.0)

    def _onDeactivate(self):
        self.setCursorSmoothAlpha(1.0, -1)

        super(DrawMagicSymbols, self)._onDeactivate()
        self.__cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.__runGameTaskChain()
        self.__runDrawTaskChain()

    def _restoreEnigma(self):
        self.__runGameTaskChain()
        self.__runDrawTaskChain()

    def _stopEnigma(self):
        self.__disableTCs()

    def _resetEnigma(self):
        if self.b_block_reseting.getValue() is True:
            return

        self.b_block_reseting.setValue(True)

        if self.symbols_appear_all_at_once:
            self.__setCurrentSymbol(None)

        else:
            symbol = self.getNextSymbol(None)
            self.__setCurrentSymbol(symbol)

        for symbol in self.symbols:
            symbol.setMoviesDefaultStates()
            symbol.complete = False

        if self.params.use_background_timer_game_rule:
            self.background_timer.changeMovie(None, self.background_timer.movie_timer, False)

        self.main_tc_semaphore.setValue(False)
        self.draw_tc_semaphore.setValue(False)

        self.b_block_reseting.setValue(False)

    def __scopeSkipEnigmaSymbolsOneByOne(self, skip_source):
        symbols = self.getSymbols(filter_='NotCompleted')

        if len(symbols) == 0:
            return

        skip_source.addFunction(self.__setCurrentSymbol, symbols[0])

        for _ in symbols:
            skip_source.addScope(self.__scopeAutoDraw)
            skip_source.addScope(self.__scopeSymbolComplete)

    def __scopeSkipEnigmaSymbolsAllAtOnce(self, skip_source):
        symbols = self.getSymbols(filter_='NotCompleted')

        for symbol in symbols:
            skip_source.addFunction(self.__setCurrentSymbol, symbol)
            skip_source.addScope(self.__scopeAutoDraw)
            skip_source.addScope(self.__scopeSymbolComplete)

    def _skipEnigmaScope(self, skip_source):
        if self.__tc_main is not None:
            self.__tc_main.cancel()
            self.__tc_main = None

        if self.__tc_draw is not None:
            self.__tc_draw.cancel()
            self.__tc_draw = None

        if self.symbols_appear_all_at_once is True:
            skip_source.addScope(self.__scopeSkipEnigmaSymbolsAllAtOnce)
        else:
            skip_source.addScope(self.__scopeSkipEnigmaSymbolsOneByOne)

        if self.params.use_background_timer_game_rule:
            skip_source.addScope(self.background_timer.changeMovie, self.background_timer.movie_win)