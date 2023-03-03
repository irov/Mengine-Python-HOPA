from Event import Event
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.DrawMagicSymbolsFightManager import DrawMagicSymbolsFightManager
from Holder import Holder


Enigma = Mengine.importEntity("Enigma")

ENIGMA_NAME_HOLDER = Holder()

MSG_SYMBOL_MOVIE_SOCKET_404 = "Enigma DrawMagicSymbolsFight '{}' error in create Symbol instance: not found socket {} in movie {}"

# consts
SHAKE_FX_SYMBOL_SLOT = "symbol"
SYMBOL_SHAKE_FX_ANCHOR_SLOT = "shake_fx"


class SoundHandler(object):
    def __init__(self, obj, delay, sound_notifier):
        self.obj = obj

        self.delay = delay
        self.sound_notifier = sound_notifier

        self.tc = None
        self.semaphore_gate = None

    def setGateOpen(self, val):
        self.semaphore_gate.setValue(val)

    def runSoundHandlerTC(self):
        self.semaphore_gate = Semaphore(False, "DrawMagicSymbolsFight_SoundHandler_Gate" + str(self.sound_notifier))

        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            tc.addSemaphore(self.semaphore_gate, From=True)
            tc.addNotify(Notificator.onSoundEffectOnObject, self.obj, self.sound_notifier)
            tc.addDelay(self.delay)

    def cancelSoundHandlerTC(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None


class Symbol(object):
    SYMBOL_ALPHA_TIME = 500.0

    def __init__(self, id_, movie, movie_complete, movie_fail, sockets, movie_shake_fx):
        self.id = id_

        self.movie = movie
        self.movie_complete = movie_complete
        self.movie_fail = movie_fail

        self.complete = False  # symbol draw is complete

        self.tc_disable = None

        '''  Setup sockets path '''
        self.s_socket_names_map = {"OneTime": [], "MultTime": []}
        self.s_socket_list = []

        ''' Setup sockets path '''
        socket_names_map_one_time_list = self.s_socket_names_map["OneTime"]
        for socket_name in sockets['OneTime']:
            socket_path_obj = self.movie.getSocket(socket_name)

            if socket_path_obj is None:
                msg = MSG_SYMBOL_MOVIE_SOCKET_404.format(ENIGMA_NAME_HOLDER.get(), socket_name, self.movie.getName())
                Trace.log("Entity", 0, msg)

                continue

            socket_names_map_one_time_list.append(socket_name)
            self.s_socket_list.append(socket_path_obj)

        socket_names_map_mult_time_list = self.s_socket_names_map["MultTime"]
        for socket_name in sockets['MultTime']:
            socket_path_obj = self.movie.getSocket(socket_name)

            if socket_path_obj is None:
                msg = MSG_SYMBOL_MOVIE_SOCKET_404.format(ENIGMA_NAME_HOLDER.get(), socket_name, self.movie.getName())
                Trace.log("Entity", 0, msg)

                continue

            socket_names_map_mult_time_list.append(socket_name)
            self.s_socket_list.append(socket_path_obj)

        self.movie_shake_fx = movie_shake_fx
        self.b_shake_fx_is_active = False

        self.__symbol_movie_sib = self.movie.getEntityNode().getSiblingNext()

        if self.__symbol_movie_sib is not None:
            self.__symbol_movie_parent = self.__symbol_movie_sib.getParent()
        else:
            self.__symbol_movie_parent = self.movie.getEntityNode().getParent()

        self.restoreAfterShakeSib = None

    def isComplete(self):
        return self.complete

    def setComplete(self, value):
        self.complete = value

    def getSocketList(self):
        return self.s_socket_list

    def checkComplete(self, socket_passed_order_list):
        SocketCanPassOneTimeOnlyList = self.s_socket_names_map["OneTime"]
        SocketCanPassMultTimeList = self.s_socket_names_map["MultTime"]

        last_socket = socket_passed_order_list[0]
        first_socket = socket_passed_order_list[len(socket_passed_order_list) - 1]

        for socket in self.s_socket_list:
            if socket not in socket_passed_order_list:
                return False

        for socket in socket_passed_order_list:
            socket_name = socket.getName()

            if socket_name in SocketCanPassOneTimeOnlyList:
                if socket_passed_order_list.count(socket) == 1:
                    continue
                elif (socket == first_socket or socket == last_socket) and (first_socket == last_socket) and socket_passed_order_list.count(socket) == 2:
                    continue
                else:
                    self.setComplete(False)
                    return False

            elif socket_name in SocketCanPassMultTimeList:
                continue

            else:
                self.setComplete(False)
                return False

        self.setComplete(True)
        return True

    def scopeAlphaEnable(self, source=None):
        if source is None:
            self.tc_disable = TaskManager.createTaskChain()

            with self.tc_disable as tc:
                tc.addEnable(self.movie)
                tc.addFunction(self.movie.setLastFrame, False)
                tc.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=0.0, To=1.0, Time=Symbol.SYMBOL_ALPHA_TIME)

        else:
            source.addEnable(self.movie)
            source.addFunction(self.movie.setLastFrame, False)
            source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=0.0, To=1.0, Time=Symbol.SYMBOL_ALPHA_TIME)

    def scopeAlphaDisable(self, source=None):
        if source is None:
            self.tc_disable = TaskManager.createTaskChain()

            with self.tc_disable as tc:
                tc.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=1.0, To=0.0, Time=Symbol.SYMBOL_ALPHA_TIME)

                tc.addDisable(self.movie)

        else:
            source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=1.0, To=0.0, Time=Symbol.SYMBOL_ALPHA_TIME)

    # -- SHAKE FX --

    def playShakeFX(self):
        if self.movie_shake_fx is None or self.b_shake_fx_is_active or self.complete:
            return

        # attach
        symbol_node = self.movie.getEntityNode()

        shake_fx_slot = self.movie_shake_fx.getMovieSlot(SHAKE_FX_SYMBOL_SLOT)
        symbol_slot = self.movie.getMovieSlot(SYMBOL_SHAKE_FX_ANCHOR_SLOT)

        if symbol_node is None or shake_fx_slot is None:
            return

        self.b_shake_fx_is_active = True

        shake_fx_slot.addChild(symbol_node)

        symbol_node.setOrigin(shake_fx_slot.getWorldPosition())
        symbol_node.setWorldPosition(symbol_slot.getWorldPosition())

        # play
        self.movie_shake_fx.setEnable(True)
        self.movie_shake_fx.setPlay(True)
        self.movie_shake_fx.setLoop(True)

    def stopShakeFX(self):
        if self.movie_shake_fx is None or not self.b_shake_fx_is_active:
            return

        # if self.__symbol_movie_sib is None:  # restore parent and order
        #     self.__symbol_movie_parent.addChild(self.movie.1EntityNode())
        # else:
        #     self.__symbol_movie_parent.addChildAfter(self.movie.getEntityNode(), self.__symbol_movie_sib)

        if self.restoreAfterShakeSib is not None:
            self.movie.getParent().getEntityNode().addChildAfter(self.movie.getEntityNode(), self.restoreAfterShakeSib)
        else:
            self.movie.returnToParent()

        self.movie.getEntityNode().setOrigin((0.0, 0.0))
        slot = self.movie.getMovieSlot(SYMBOL_SHAKE_FX_ANCHOR_SLOT)
        self.movie.getEntityNode().setWorldPosition(slot.getWorldPosition())

        self.movie_shake_fx.setPlay(False)
        self.movie_shake_fx.setLoop(False)
        self.movie_shake_fx.setEnable(False)
        # self.movie_shake_fx.setLastFrame(False)

        self.b_shake_fx_is_active = False

    def destroyShakeFX(self):
        if self.movie_shake_fx is None:
            return

        # if self.__symbol_movie_sib is None:  # restore parent and order
        #     self.__symbol_movie_parent.addChild(self.movie.getEntityNode())
        # else:
        #     self.__symbol_movie_parent.addChildAfter(self.movie.getEntityNode(), self.__symbol_movie_sib)

        if self.restoreAfterShakeSib is not None:
            self.movie.getParent().getEntityNode().addChildAfter(self.movie.getEntityNode(), self.restoreAfterShakeSib)
        else:
            self.movie.returnToParent()

        self.movie_shake_fx.removeFromParent()
        self.movie_shake_fx.onDestroy()
        self.movie_shake_fx = None

    # -- -- --


class HP(object):

    def __init__(self, movie, HP_ALPHA_TIME):
        self.movie = movie
        self.tc_disable = None
        self.HP_ALPHA_TIME = HP_ALPHA_TIME

    def scopeAlphaEnable(self, source=None):
        if source is None:
            self.tc_disable = TaskManager.createTaskChain()

            with self.tc_disable as tc:
                tc.addEnable(self.movie)
                tc.addFunction(self.movie.setLastFrame, False)
                tc.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=0.0, To=1.0, Time=self.HP_ALPHA_TIME)

        else:
            source.addEnable(self.movie)
            source.addFunction(self.movie.setLastFrame, False)
            source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=0.0, To=1.0, Time=self.HP_ALPHA_TIME)

    def scopeAlphaDisable(self, source=None):
        if source is None:
            self.tc_disable = TaskManager.createTaskChain()

            with self.tc_disable as tc:
                tc.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=1.0, To=0.0, Time=self.HP_ALPHA_TIME)

                tc.addDisable(self.movie)

        else:
            source.addTask("TaskNodeAlphaTo", Node=self.movie.getEntityNode(), From=1.0, To=0.0, Time=self.HP_ALPHA_TIME)

    def destroyHP(self):
        if self.movie is None:
            return

        self.movie.returnToParent()
        self.movie.removeFromParent()
        self.movie.onDestroy()


class DrawMagicSymbolsFight(Enigma):
    EVENT_INTERRUPT = Event("DrawMagicSymbolsInterrupt")
    EVENT_COMPLETE_DRAWING = Event("DrawMagicSymbolsCompleteDrawing")

    def __init__(self):
        super(DrawMagicSymbolsFight, self).__init__()
        self.params = None

        # main logic objects
        self.boundary = None  # movie with boundary socket
        self.symbols = list()
        self.hp = list()
        self.current_symbol = None
        # cache entered sockets then check if current socket path can complete symbol
        self.current_symbol_path_queue = list()
        #

        # main logic tc
        self.__tc_handle_interrupt = None
        self.__tc_append_socket_path = None
        self.__tc_prep = None
        self.__tc_hp_prep = None
        self.__tc_select_symbol = None
        #

        # cosmetic cursor
        self.cursor_movie = None  # movie attached to cursor
        self.__tc_smooth_alpha_cursor = None
        self.__tc_smooth_alpha_cursor_movie = None
        self.__tc_movie_cursor_movie = None
        #

        # pen drawing
        self.mouse_pos_provider = None
        self.last_mouse_pos = None

        self.drawing_node = None
        self.pen_sprites = []
        self.pen_sprites_destroy_queue = []

        self.b_key_pressed = False
        self.pen_offset = Mengine.vec3f(0.0, 0.0, 0.0)

        self.draw_sound_handler = None
        #

        # fight movies
        self.fight_movies = {}
        self.fail_movie = None
        self.current_fight_movie = None
        self.current_fight_movie_index = 0  #

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParams(self):
        self.params = DrawMagicSymbolsFightManager.getParam(self.EnigmaName)
        Symbol.SYMBOL_ALPHA_TIME = self.params.symbol_movie_alpha_time

        ENIGMA_NAME_HOLDER.set(self.EnigmaName)

    def __setup(self):
        GET_OBJ = self.object.getObject
        HAS_OBJ = self.object.hasObject

        ''' creating mg objects '''
        # create symbols instances
        symbols = list()

        symbol_complete_params = self.params.symbols_complete
        symbol_fail_params = self.params.symbols_fail
        symbol_shake_params = self.params.symbols_shake_fx
        self.symbols_location_type = self.params.symbols_location_type
        self.boundary = GET_OBJ(self.params.boundary)

        for symbol_movie_name, sockets in self.params.symbols:
            symbol_movie = GET_OBJ(symbol_movie_name)

            symbol_complete_movie_name = symbol_complete_params[symbol_movie_name]

            if HAS_OBJ(symbol_complete_movie_name):
                symbol_complete_movie = GET_OBJ(symbol_complete_movie_name)

            else:
                symbol_complete_movie = None

            symbol_fail_movie_name = symbol_fail_params[symbol_movie_name]

            if HAS_OBJ(symbol_fail_movie_name):
                symbol_fail_movie = GET_OBJ(symbol_fail_movie_name)

            else:
                symbol_fail_movie = None

            if self.symbols_location_type is not None and self.symbols_location_type is True:
                slot = self.boundary.getEntity().getMovieSlot("centre")
                node_symbol = symbol_movie.getEntityNode()
                slot.addChild(node_symbol)
            else:
                slot = symbol_movie.getEntity().getMovieSlot(SYMBOL_SHAKE_FX_ANCHOR_SLOT)
                node_symbol = symbol_movie.getEntityNode()
                node_symbol.setLocalPosition(slot.getWorldPosition())

            # symbol shake fx
            movie_shake_fx_name = symbol_shake_params[symbol_movie_name]
            movie_shake_fx = None
            if movie_shake_fx_name is not None:
                movie_shake_fx = self.object.generateObjectUnique(movie_shake_fx_name + symbol_movie_name,
                                                                  movie_shake_fx_name, Enable=True)
                node_movie_shake_fx = movie_shake_fx.getEntityNode()
                self.addChild(node_movie_shake_fx)

                slot = symbol_movie.getEntity().getMovieSlot(SYMBOL_SHAKE_FX_ANCHOR_SLOT)
                if slot is not None:
                    node_movie_shake_fx.setLocalPosition(slot.getWorldPosition())

            movie_hp_name = self.params.hp_movie_name
            movie_hp = None
            if movie_hp_name is not None:
                movie_hp = self.object.generateObjectUnique(movie_hp_name + symbol_movie_name, movie_hp_name, Enable=True)
                slot_name = symbol_movie_name.replace("Movie2_", "")
                slot = self.boundary.getEntity().getMovieSlot(slot_name)
                movie_hp_node = movie_hp.getEntityNode()
                slot.addChild(movie_hp_node)
                hp = HP(movie_hp, self.params.hp_alpha_time)
                self.hp.append(hp)

            symbol = Symbol(symbol_movie_name, symbol_movie, symbol_complete_movie, symbol_fail_movie, sockets, movie_shake_fx)

            symbols.append(symbol)

        self.symbols = symbols
        #

        if self.symbols_location_type is not None and self.symbols_location_type is True:
            for symbol in self.symbols[1:]:
                symbol.movie.setEnable(False)

        ''' Creating Node For Sprite_Pen objects'''
        if self.object.hasPrototype(self.params.pen_sprite_prot):
            self.drawing_node = Mengine.createNode("Interender")
            self.drawing_node.setName('Drawing Node')
            self.node.addChild(self.drawing_node)
            self.drawing_node.setLocalPosition((0.0, 0.0))

            ''' Setup Sprite_Pen generation callback on cursor position change '''
            self.mouse_pos_provider = Mengine.addMousePositionProvider(None, None, None,
                                                                       self.onMouseChangeGeneratePenSprite)

            ''' Create Draw Sound Handler '''
            self.draw_sound_handler = SoundHandler(self.object, self.params.draw_sound_delay,
                                                   self.params.draw_sound_notifier)

            ''' Symbol shake fx restore add children after sibling resolve'''
            for symbol in self.symbols:
                symbol.restoreAfterShakeSib = self.drawing_node

        else:
            Trace.log("Entity", 0, "Not Found SpritePenPrototype with name: %s, Please Add!!" % self.params.pen_sprite_prot)

        ''' Fail Movie '''
        self.fail_movie = GET_OBJ(self.params.fail_movie)

        ''' Init Fight Movies '''
        GET_OBJ = self.object.getObject

        fight_movies = dict()
        for index_, (movie_fight_name, movie_idle_name) in enumerate(self.params.fight_movies):
            movie_fight = GET_OBJ(movie_fight_name)
            movie_fight.setEnable(False)

            movie_idle = GET_OBJ(movie_idle_name)
            movie_idle.setEnable(False)

            fight_movies[index_] = (movie_fight, movie_idle)

        self.fight_movies = fight_movies
        self.current_fight_movie_index = 0

        fight_movie_idle = self.fight_movies[self.current_fight_movie_index][1]
        fight_movie_idle.setEnable(True)
        fight_movie_idle.setPlay(True)
        fight_movie_idle.setLoop(True)

        ''' initialize cursor movie '''
        cursor_movie_name = self.params.cursor
        if HAS_OBJ(cursor_movie_name):
            self.cursor_movie = GET_OBJ(cursor_movie_name)
            self.cursor_movie.setAlpha(0.0)
            self.cursor_movie.getEntityNode().setLocalPosition(Mengine.getCursorPosition())
            self.addChild(self.cursor_movie.getEntityNode())

    def __disableTCs(self):
        for symbol in self.symbols:
            if symbol.tc_disable is not None:
                symbol.tc_disable.cancel()
                symbol.tc_disable = None

        for hp in self.hp:
            if hp.tc_disable is not None:
                hp.tc_disable.cancel()
                hp.tc_disable = None

        # main tcs
        if self.__tc_append_socket_path is not None:
            self.__tc_append_socket_path.cancel()
            self.__tc_append_socket_path = None

        if self.__tc_prep is not None:
            self.__tc_prep.cancel()
            self.__tc_prep = None

        if self.__tc_hp_prep is not None:
            self.__tc_hp_prep.cancel()
            self.__tc_hp_prep = None

        if self.__tc_select_symbol is not None:
            self.__tc_select_symbol.cancel()
            self.__tc_select_symbol = None

        if self.__tc_handle_interrupt is not None:
            self.__tc_handle_interrupt.cancel()
            self.__tc_handle_interrupt = None
        #

        # optional cosmetic cursor
        if self.__tc_smooth_alpha_cursor is not None:
            self.__tc_smooth_alpha_cursor.cancel()
            self.__tc_smooth_alpha_cursor = None

        if self.__tc_smooth_alpha_cursor_movie is not None:
            self.__tc_smooth_alpha_cursor_movie.cancel()
            self.__tc_smooth_alpha_cursor_movie = None

        if self.__tc_movie_cursor_movie is not None:
            self.__tc_movie_cursor_movie.cancel()
            self.__tc_movie_cursor_movie = None
        #

        # draw sound tc
        if self.draw_sound_handler:
            self.draw_sound_handler.cancelSoundHandlerTC()  #

    def __cleanUp(self):
        self.setCursorSmoothAlpha(1.0, -1)

        # destroy shake fx
        for symbol in self.symbols:
            symbol.destroyShakeFX()

        for hp in self.hp:
            hp.destroyHP()

        del self.hp[:]

        self.__disableTCs()

        if self.mouse_pos_provider is not None:
            Mengine.removeMousePositionProvider(self.mouse_pos_provider)
            self.mouse_pos_provider = None

        self.__destroyPen()

        if self.drawing_node is not None:
            self.drawing_node.removeFromParent()
            Mengine.destroyNode(self.drawing_node)
            self.drawing_node = None

    # -------------- Pen Sprite Create/Destroy Handle ------------------------------------------------------------------
    def onMouseChangeGeneratePenSprite(self, _touch_id, pos):
        """
        This method called every frame, so if cursor moved to far from pos in last frame then we should generate
        multiple pen sprites.
        """

        if not self.b_key_pressed:
            return

        if self.last_mouse_pos is None:  # first sprite handle
            self.last_mouse_pos = pos
            self.__createPen(pos)
            return

        self.draw_sound_handler.setGateOpen(True)  # open gate to allow play draw sound

        # handle sprites creation
        distance = Mengine.length_v2_v2(self.last_mouse_pos, pos)
        temp_distance = distance

        if distance < self.params.draw_offset or distance > self.params.draw_distance_stop:
            self.__createPen(pos)

        else:
            self.__createPen(pos)

            while temp_distance > self.params.draw_offset:
                temp_distance -= self.params.draw_offset
                t = 1.0 - temp_distance / distance

                # x coord for point on line (last_pos, new_pos) with t [0, 1] offset
                x = (1.0 - t) * self.last_mouse_pos.x + t * pos.x

                # y coord for point on line (last_pos, new_pos) with t [0, 1] offset
                y = (1.0 - t) * self.last_mouse_pos.y + t * pos.y

                self.__createPen((x, y))

        if len(self.pen_sprites) > self.params.max_draw_distance:
            self.pen_sprites[0].removeFromParent()
            self.pen_sprites[0].onDestroy()
            del self.pen_sprites[0]

        self.last_mouse_pos = pos

        self.draw_sound_handler.setGateOpen(False)  # close gate to disallow play draw sound  #

    def __createPen(self, pos):
        sprite_pen = self.object.generateObjectUnique("Sprite_Pen_%d" % len(self.pen_sprites),
                                                      self.params.pen_sprite_prot, Enable=True)

        sprite_pen.removeFromParent()

        if "Movie2" in self.params.pen_sprite_prot:
            sprite_pen_en = sprite_pen.getEntityNode()
            self.drawing_node.addChild(sprite_pen_en)
            sprite_pen_en.setWorldPosition(pos)
        else:
            sprite_pen_en = sprite_pen.entity.node
            self.drawing_node.addChild(sprite_pen_en)
            sprite_pen_en.setWorldPosition(pos + self.pen_offset)

        if self.params.rotate_pen_sprite is True:
            sprite_pen_en.setAngle(Mengine.rand(360))

        self.pen_sprites.append(sprite_pen)

    def __destroyPen(self):
        for sprite_pen in self.pen_sprites:
            sprite_pen.removeFromParent()
            sprite_pen.onDestroy()

        self.pen_sprites = []

        self.last_mouse_pos = None

    # -------------- Getters Setters Checkers Handlers -----------------------------------------------------------------
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

    def scopeHandleCurrentSymbolComplete(self, source):
        if self.current_symbol is None or self.current_symbol.isComplete():  # if was already complete do nothing
            return

        is_complete = self.current_symbol.checkComplete(self.current_symbol_path_queue)

        if is_complete:
            # normal case, on each completed symbol played idle/fight anim
            with GuardBlockInput(source) as source_1:
                if self.current_fight_movie_index < len(self.fight_movies):
                    # disable current idle movie
                    current_idle_movie = self.fight_movies[self.current_fight_movie_index][1]
                    source_1.addTask("TaskNodeAlphaTo", Node=current_idle_movie.getEntityNode(), To=0.0,
                                     Time=self.params.fight_movies_alpha_time, IsTemp=True)
                    source_1.addDisable(current_idle_movie)

                    # enable current fight movie
                    self.current_fight_movie = self.fight_movies[self.current_fight_movie_index][0]
                    source_1.addEnable(self.current_fight_movie)
                    source_1.addTask("TaskNodeAlphaTo", Node=self.current_fight_movie.getEntityNode(), From=0.0, To=1.0,
                                     Time=self.params.fight_movies_alpha_time, IsTemp=True)

                    self.current_fight_movie_index += 1

                    with source_1.addParallelTask(3) as (parallel_0, parallel_1, parallel_2):
                        # play current play movie
                        parallel_0.addPlay(self.current_fight_movie)

                        if self.current_fight_movie_index < len(self.fight_movies):  # enable next idle only if not last
                            # disable current fight movie
                            parallel_0.addTask("TaskNodeAlphaTo", Node=self.current_fight_movie.getEntityNode(), To=0.0,
                                               Time=self.params.fight_movies_alpha_time, IsTemp=True)
                            parallel_0.addDisable(self.current_fight_movie)

                            # loop-play next idle movie
                            next_idle = self.fight_movies[self.current_fight_movie_index][1]
                            parallel_0.addEnable(next_idle)
                            parallel_0.addTask("TaskNodeAlphaTo", Node=next_idle.getEntityNode(), From=0.0, To=1.0,
                                               Time=self.params.fight_movies_alpha_time, IsTemp=True)
                            parallel_0.addPlay(next_idle, Wait=False, Loop=True)

                        parallel_1.addScope(self.scopeDecreaseHP)
                        parallel_2.addPlay(self.current_symbol.movie)


                else:  # case when we have more symbols then fight/idle anims
                    with source_1.addParallelTask(2) as (parallel_0, parallel_1):
                        parallel_0.addPlay(self.current_symbol.movie)
                        parallel_1.addScope(self.scopeDecreaseHP)

                # current symbol movie disable
                if self.symbols.index(self.current_symbol) + 1 == len(self.symbols):  # wait last
                    source_1.addScope(self.current_symbol.scopeAlphaDisable)
                else:
                    source_1.addFunction(self.current_symbol.scopeAlphaDisable)
                    if self.symbols_location_type is not None and self.symbols_location_type is True:
                        symbol = self.symbols[self.symbols.index(self.current_symbol) + 1]
                        source_1.addFunction(symbol.scopeAlphaEnable)

        else:
            # symbol not complete, play fail movie
            source.addPlay(self.fail_movie, AutoEnable=True)

    def scopeDecreaseHP(self, source):
        if len(self.hp) != 0:
            source.addPlay(self.hp[-1].movie, Wait=True, Loop=False)
            source.addScope(self.hp[-1].scopeAlphaDisable)

            source.addFunction(self.hp[-1].destroyHP)
            source.addFunction(self.hp.remove, self.hp[-1])

    def checkAllSymbolsComplete(self):
        symbols = self.getSymbols('NotCompleted')

        if len(symbols) == 0:
            return True
        return False

    def handleAllSymbolsComplete(self):
        if self.checkAllSymbolsComplete() and self.EVENT_INTERRUPT is not None:
            self.EVENT_INTERRUPT()

    def __setCurrentSymbol(self, symbol):
        self.current_symbol = symbol

    # -------------- [Cosmetic] Cursor scopes --------------------------------------------------------------------------
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

    # -------------- [Cosmetic] Symbol Shake FX ------------------------------------------------------------------------
    def __playSymbolsShakeFX(self):
        for symbol in self.symbols:
            if symbol == self.current_symbol:
                continue
            symbol.playShakeFX()

    def __stopSymbolsShakeFX(self):
        for symbol in self.symbols:
            if symbol == self.current_symbol:
                continue
            symbol.stopShakeFX()

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def __onSocketEnterEventInit(self, movie_obj, name, hotspot, x, y):
        self.current_symbol_path_queue = [hotspot]

        return True  # dispatch one time only

    def __onSocketEnterEventAppend(self, movie_obj, name, hotspot, x, y):
        self.current_symbol_path_queue.append(hotspot)

        return True  # dispatch one time only

    def __scopeInitSocketPath(self, source):
        source.addEvent(self.EVENT_COMPLETE_DRAWING)

        with source.addRepeatTask() as (repeat, until):
            for (symbol, race) in repeat.addRaceTaskList(self.symbols):
                race.addEvent(symbol.movie.onMovieSocketEnterEvent, self.__onSocketEnterEventInit)
                race.addFunction(self.__setCurrentSymbol, symbol)
            until.addTask("TaskMouseButtonClick", isDown=True)

    def __scopeAppendSocketPath(self, source):
        movies = [symbol.movie for symbol in self.symbols] + [self.boundary]
        for (movie, source) in source.addRaceTaskList(movies):
            source.addEvent(movie.onMovieSocketEnterEvent, self.__onSocketEnterEventAppend)

    def __InitSelectSymbolTC(self):
        if self.__tc_select_symbol is not None:  # check
            self.__tc_select_symbol.cancel()

        self.__tc_select_symbol = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_select_symbol as tc:
            tc.addScope(self.__scopeInitSocketPath)

    def __initAppendSocketPathTC(self):
        self.b_key_pressed = False

        if self.__tc_append_socket_path is not None:  # check
            self.__tc_append_socket_path.cancel()

        self.__tc_append_socket_path = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_append_socket_path as tc:
            def setIsPressed(val):
                self.b_key_pressed = val

            tc.addTask("TaskMouseButtonClick", isDown=True)
            tc.addFunction(setIsPressed, True)
            if self.symbols_location_type is None or self.symbols_location_type is False:
                tc.addFunction(self.__playSymbolsShakeFX)

            with tc.addRepeatTask() as (repeat, until):
                repeat.addScope(self.__scopeAppendSocketPath)
                until.addTask("TaskMouseButtonClick", isDown=False)
                until.addFunction(self.EVENT_COMPLETE_DRAWING)

            tc.addFunction(setIsPressed, False)
            tc.addFunction(self.__destroyPen)  # destroy all created sprites
            if self.symbols_location_type is None or self.symbols_location_type is False:
                tc.addFunction(self.__stopSymbolsShakeFX)
            tc.addScope(self.scopeHandleCurrentSymbolComplete)
            tc.addFunction(self.handleAllSymbolsComplete)

    def __initHandleInterruptTC(self):
        if self.__tc_handle_interrupt is not None:  # check
            self.__tc_handle_interrupt.cancel()

        self.__tc_handle_interrupt = TaskManager.createTaskChain()
        with self.__tc_handle_interrupt as tc:
            tc.addEvent(self.EVENT_INTERRUPT)

            ''' Handle On Interrupt Gameplay Events '''
            with tc.addIfTask(self.checkAllSymbolsComplete) as (true, false):
                true.addFunction(self.enigmaComplete)
                false.addFunction(self._resetEnigma)

    def __initPrepTC(self):
        if self.__tc_prep is not None:  # check
            self.__tc_prep.cancel()

        self.__tc_prep = TaskManager.createTaskChain()
        with self.__tc_prep as tc:
            ''' Smooth Symbol Appearing '''
            if self.symbols_location_type is None or self.symbols_location_type is False:
                for symbol, parallel in tc.addParallelTaskList(self.symbols):
                    parallel.addScope(symbol.scopeAlphaEnable)
            else:
                tc.addScope(self.symbols[0].scopeAlphaEnable)

    def __initHPPrepTC(self):
        if self.__tc_hp_prep is not None:  # check
            self.__tc_hp_prep.cancel()

        self.__tc_hp_prep = TaskManager.createTaskChain()
        with self.__tc_hp_prep as tc:
            ''' Smooth HP Appearing '''
            for hp, parallel in tc.addParallelTaskList(self.hp):
                parallel.addScope(hp.scopeAlphaEnable)

    def __runTaskChain(self):
        """"""

        ''' Init TC SELECT SYMBOL '''
        self.__InitSelectSymbolTC()
        self.EVENT_COMPLETE_DRAWING()

        ''' Init TC HANDLE INTERRUPT '''
        self.__initHandleInterruptTC()

        ''' Init TC PREP '''
        self.__initPrepTC()

        if len(self.hp) != 0:
            '''Init TC HP PREP'''
            self.__initHPPrepTC()

        ''' Init TC DRAW '''
        self.__initAppendSocketPathTC()

        ''' Enable Draw Sound Handler '''
        if self.draw_sound_handler is not None:
            self.draw_sound_handler.runSoundHandlerTC()

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(DrawMagicSymbolsFight, self)._onPreparation()
        self._loadParams()
        self.__setup()

    def __cursorHandleOnActivate(self):
        with TaskManager.createTaskChain() as tc:
            tc.addDelay(1)  # fix for setCursorSmoothAlpha error in case of resumeEnigma

            tc.addFunction(self.enableMoveCursorMovieTC, True)
            tc.addFunction(self.setCursorMovieSmoothAlpha, 1.0)
            tc.addFunction(self.setCursorSmoothAlpha, 0.0)

    def _onActivate(self):
        super(DrawMagicSymbolsFight, self)._onActivate()

        self.__cursorHandleOnActivate()

        ''' cursor offset '''
        if "Movie2" not in self.params.pen_sprite_prot:
            temp_sprite = self.object.generateObjectUnique(self.params.pen_sprite_prot + 'tmp', self.params.pen_sprite_prot)
            size = temp_sprite.entity.getSize()
            self.pen_offset.x, self.pen_offset.y = -size.x / 2, -size.y / 2
            temp_sprite.onDestroy()

    def _onDeactivate(self):
        self.setCursorSmoothAlpha(1.0, -1)

        super(DrawMagicSymbolsFight, self)._onDeactivate()

        self.__cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.__runTaskChain()

    def _restoreEnigma(self):
        self.__runTaskChain()

    def _stopEnigma(self):
        self.__disableTCs()

    def _resetEnigma(self):
        self.__cleanUp()
        self.__setup()
        self.__cursorHandleOnActivate()
        self.__runTaskChain()

    def _skipEnigmaScope(self, skip_source):
        pass
