import re

from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.CursorManager import CursorManager
from HOPA.SpellsManager import SpellsManager
from HOPA.System.SystemSpells import SystemSpells
from Notification import Notification

ERROR_MSG_TEXT_ALIAS_404 = 'MOVIE FROM PROTO "{}" CANT FIND TEXT ALIAS "{}" FOR TEXT "{}"'
ERROR_MSG_TEXT_ID_404 = 'CANT FIND TEXT ID "{}" IN Texts.xml FOR MOVIE "{}"'

class AmuletPowerButton(object):
    SPELL_AMULET_OBJECT = None
    AMULET = None

    # amulet stone button states
    APPEAR = 'appear'  # resolved in SystemSpells and in onPreparation
    IDLE = 'idle'  # resolved in SystemSpells and in onPreparation
    READY = 'ready'  # resolved in SystemSpells
    SELECT = 'select'  # resolved in SystemSpells

    # amulet power use movies
    AIM = 'aim'  # resolved in systemSpells
    FAIL = 'fail'  # resolved in systemSpells

    # texts
    INFO = 'info'
    LOCKED = 'locked'

    # SpellsManager params
    SOCKET_NAME = 'socket'
    ALIAS_POWER_DESC = '$AliasPowerLocked'
    ALIAS_POWER_LOCKED = '$AliasPowerDescription'
    HINT_TEXT_ALPHA_TIME = 400
    HINT_TEXT_SHOW_TIME = 1000
    AMULET_USE_ALPHA_TIME = -1

    # deprecated: EVENT_STATE_UPDATE = Event('AmuletPowerButton_MovieStateUpdate_Event')
    NOTIFICATOR_ButtonStateChange = Notificator.onSpellAmuletPowerButtonStateChange

    def __init__(self, sys_spell_amulet_stone):
        amulet_stone_param = sys_spell_amulet_stone.param
        power_type = amulet_stone_param.power_type

        self.sys_spell_amulet_stone = sys_spell_amulet_stone
        self.power_type = power_type

        ''' Movies Creation '''
        object_generator = self.SPELL_AMULET_OBJECT.generateObjectUnique

        appear_proto_name = amulet_stone_param.movie2_power_stone_prototype_appear
        idle_proto_name = amulet_stone_param.movie2_power_stone_prototype_idle
        ready_proto_name = amulet_stone_param.movie2_power_stone_prototype_ready
        select_proto_name = amulet_stone_param.movie2_power_stone_select
        info_proto_name = amulet_stone_param.movie2_power_stone_info_type
        locked_proto_name = amulet_stone_param.movie2_power_stone_locked_info_prototype
        aim_proto_name = amulet_stone_param.movie2_power_stone_aim_prototype
        fail_proto_name = amulet_stone_param.movie2_power_stone_fail_prototype
        first_submovie_name = amulet_stone_param.movie2_power_aim_first_submovie
        second_submovie_name = amulet_stone_param.movie2_power_aim_second_submovie
        third_submovie_name = amulet_stone_param.movie2_power_aim_third_submovie

        self.movies_states_buttons = {AmuletPowerButton.APPEAR: object_generator(power_type + appear_proto_name, appear_proto_name), AmuletPowerButton.IDLE: object_generator(power_type + idle_proto_name, idle_proto_name), AmuletPowerButton.READY: object_generator(power_type + ready_proto_name, ready_proto_name), AmuletPowerButton.SELECT: object_generator(power_type + select_proto_name, select_proto_name)}

        self.movies_info = {AmuletPowerButton.INFO: object_generator(power_type + info_proto_name, info_proto_name),

            AmuletPowerButton.LOCKED: object_generator(power_type + locked_proto_name, locked_proto_name)}

        self.movies_use = {AmuletPowerButton.AIM: object_generator(power_type + aim_proto_name, aim_proto_name), AmuletPowerButton.FAIL: object_generator(power_type + fail_proto_name, fail_proto_name)}

        movie_aim = self.movies_use[AmuletPowerButton.AIM]
        movie_entity = movie_aim.getEntity()
        first_submovie = movie_entity.getSubMovie(first_submovie_name)
        second_submovie = movie_entity.getSubMovie(second_submovie_name)
        third_submovie = movie_entity.getSubMovie(third_submovie_name)

        self.rune_submovies = {re.findall('(?<=_).*$', first_submovie_name)[0].lower(): first_submovie, re.findall('(?<=_).*$', second_submovie_name)[0].lower(): second_submovie, re.findall('(?<=_).*$', third_submovie_name)[0].lower(): third_submovie}

        for value in self.rune_submovies.values():
            value.setEnable(False)

        spell_amulet_entity_node = AmuletPowerButton.SPELL_AMULET_OBJECT.getEntityNode()
        for movie in self.movies_use.values():
            node = movie.getEntityNode()
            spell_amulet_entity_node.addChild(node)

        self.movies = dict(self.movies_states_buttons)
        self.movies.update(self.movies_info)
        self.movies.update(self.movies_use)

        ''' Setup default movie states '''
        for obj_movie in self.movies.values():
            obj_movie.setEnable(False)
            obj_movie.setPlay(False)

        self.cur_button_movie = self.movies_states_buttons[AmuletPowerButton.APPEAR]
        self.cur_button_state = self.getStateUpdate()

        play_and_loop = self.cur_button_state is AmuletPowerButton.IDLE
        self.changeState(self.cur_button_state, play_and_loop, play_and_loop)

        ''' Setup texts '''
        self.__setupTextIDs()

        ''' Register AmultetPowerButton Instance in Amulet '''
        self.AMULET.addPowerButton(power_type, self)

        ''' Handle Movies Attachment to Amulet'''
        self.attachMoviesToAmuletObjCurStateMovie()

        ''' Data for handling movie_info alpha in/out '''
        self.current_movie_info = None
        self.__restoreInfoMovies()
        self.b_show_info_on_cursor_enabled = False
        self.b_show_info_on_timer_active = False
        self.__tc_show_info_alpha_in = None
        self.__tc_show_info_alpha_out = None
        self.__tc_show_info_handler = None

    def __setupTextIDs(self):
        """
        Try setup text, else show error msg
        """
        text_env = str(self.power_type)

        movie_info = self.movies_info[self.INFO]
        movie_info.setTextAliasEnvironment(text_env)

        movie_locked = self.movies_info[self.LOCKED]
        movie_locked.setTextAliasEnvironment(text_env)

        param = self.sys_spell_amulet_stone.param

        id_text_power_desc = param.text_id_for_alias_power_description
        id_text_power_locked = param.text_id_for_alias_power_locked

        alias_power_locked = AmuletPowerButton.ALIAS_POWER_LOCKED
        alias_power_desc = AmuletPowerButton.ALIAS_POWER_DESC

        if movie_locked.entity.hasMovieText(alias_power_locked):
            if Mengine.existText(id_text_power_locked):
                Mengine.setTextAlias(text_env, alias_power_locked, id_text_power_locked)
            else:
                Trace.log("Entity", 1, ERROR_MSG_TEXT_ID_404.format(id_text_power_locked, movie_locked))
        else:
            Trace.log("Entity", 1, ERROR_MSG_TEXT_ALIAS_404.format(movie_locked.getName(), alias_power_locked, id_text_power_locked))

        if movie_info.entity.hasMovieText(alias_power_desc):
            if Mengine.existText(id_text_power_desc):
                Mengine.setTextAlias(text_env, alias_power_desc, id_text_power_desc)
            else:
                Trace.log("Entity", 1, ERROR_MSG_TEXT_ID_404.format(id_text_power_desc, movie_info))
        else:
            Trace.log("Entity", 1, ERROR_MSG_TEXT_ALIAS_404.format(movie_info.getName(), alias_power_desc, id_text_power_desc))

    def getMoviesStatesButtons(self):
        return self.movies_states_buttons

    def changeSubmovieState(self, state, name):
        submovie = self.rune_submovies[name]
        submovie.setEnable(state)

    def getSubmovies(self):
        return self.rune_submovies

    def attachMoviesToAmuletObjCurStateMovie(self):
        """
        init
        :return:
        """
        param = self.sys_spell_amulet_stone.param

        stone_slot_name = param.amulet_stone_slot_name
        info_slot_name = param.amulet_info_slot_name

        self.AMULET.addButtonToCurMovieStateSlot(stone_slot_name, self.movies_states_buttons[AmuletPowerButton.APPEAR], self.movies_states_buttons[AmuletPowerButton.IDLE], self.movies_states_buttons[AmuletPowerButton.READY], self.movies_states_buttons[AmuletPowerButton.SELECT])

        self.AMULET.addButtonToCurMovieStateSlot(info_slot_name, self.movies_info[AmuletPowerButton.INFO], self.movies_info[AmuletPowerButton.LOCKED])

    # MOVIE STATES BLOCK ///////////////////////////////////////////////////////////////////////////////////////////////
    def changeState(self, state, play=None, loop=None, last_frame=None):
        self.cur_button_movie.setEnable(False)

        new_cur_movie = self.movies_states_buttons[state]
        new_cur_movie.setEnable(True)

        # print("current movie is {}, new current movie is {}".format(self.cur_button_movie.getName(), new_cur_movie.getName()))

        if play is not None:
            new_cur_movie.setPlay(play)
        if loop is not None:
            new_cur_movie.setLoop(loop)
        if last_frame is not None:
            new_cur_movie.setLastFrame(last_frame)

        self.cur_button_movie = new_cur_movie

        self.cur_button_state = state
        Notification.notify(self.NOTIFICATOR_ButtonStateChange, self, state)

    def getStateUpdate(self):
        """
        Try to get correct movie state from System param etc.
        :return: movie state key from self.movies dict
        """
        if self.sys_spell_amulet_stone.getLocked():
            return AmuletPowerButton.APPEAR
        else:
            return AmuletPowerButton.IDLE

    def scopePlayCurState(self, source, **params):
        if self.cur_button_movie.getEntity().isActivate() is True:
            source.addPlay(self.cur_button_movie, **params)

    def scopePlayAmuletUse(self, source, power_use_movie_type, play_hide_amulet_after_use=False):
        amulet = AmuletPowerButton.AMULET
        power_use_movie = self.movies_use[power_use_movie_type]
        en_power_use_movie = power_use_movie.getEntityNode()
        time = self.AMULET_USE_ALPHA_TIME

        source.addNotify(amulet.NOTIFICATOR_AmuletStateChange, self.AIM)  # show_info fix
        source.addFunction(amulet.setEnableCurrentAmuletMovie, False)

        source.addEnable(power_use_movie)

        if time != -1:
            source.addTask("TaskNodeAlphaTo", Node=en_power_use_movie, To=1.0, From=0.0, Time=time)

        source.addPlay(power_use_movie)

        if time != -1:
            source.addTask("TaskNodeAlphaTo", Node=en_power_use_movie, To=0.0, Time=time)

        source.addDisable(power_use_movie)

        source.addFunction(amulet.setEnableCurrentAmuletMovie, True)

        source.addScope(amulet.scopeCloseAmulet, skip_play=not play_hide_amulet_after_use)

    def scopeClick(self, source):
        source.addScope(self.__scopeDynamicCurrentMovieSocketTask, "TaskMovie2SocketClick")

    def scopeEnter(self, source):
        source.addScope(self.__scopeDynamicCurrentMovieSocketTask, "TaskMovie2SocketEnter")

    def scopeLeave(self, source):
        source.addScope(self.__scopeDynamicCurrentMovieSocketTask, "TaskMovie2SocketLeave")

    def scopeChangeCursorMode(self, source):
        source.addScope(self.scopeEnter)
        source.addFunction(CursorManager.setCursorMode, "UseItem")
        source.addScope(self.scopeLeave)
        source.addFunction(CursorManager.setCursorMode, "Default")

    def unlockFilter(self, power_type, *args):
        return self.power_type == power_type

    # Dynamic Socket Task  /////////////////////////////////////////////////////////////////////////////////////////////
    def __scopeCurrentMovieSocketTask(self, source, task, semaphore, **params):
        if not (task == "TaskMovie2SocketEnter" or task == "TaskMovie2SocketLeave" or task == "TaskMovie2SocketClick"):
            Trace.log("Entity", 0, "AmuletPowerButton::__scopeCurrentMovieSocketTask: Unknown task %s" % task)
            return

        if self.cur_button_movie is None:
            source.addBlock()
            return

        if not self.cur_button_movie.getEnable():
            source.addBlock()
            return

        source.addTask(task, Movie2=self.cur_button_movie, SocketName=AmuletPowerButton.SOCKET_NAME, **params)
        source.addSemaphore(semaphore, To=True)

    def __scopeDynamicCurrentMovieSocketTask(self, source, task, **params):
        """
        Dynamic socket task, when state updated, new socket clicked task is appeared
        """
        semaphore = Semaphore(False, self.power_type)

        with source.addRepeatTask() as (repeat, until):
            with repeat.addRaceTask(2) as (race_0, race_1):
                race_0.addListener(AmuletPowerButton.NOTIFICATOR_ButtonStateChange, lambda obj, state: obj is self)
                race_1.addScope(self.__scopeCurrentMovieSocketTask, task, semaphore, **params)

            until.addSemaphore(semaphore, From=True)

    # INFO MOVIE BLOCK /////////////////////////////////////////////////////////////////////////////////////////////////
    def __updateCurrentInfoMovie(self):
        if self.sys_spell_amulet_stone.getLocked():
            new_movie_info = self.movies_info[self.LOCKED]
        else:
            new_movie_info = self.movies_info[self.INFO]

        if not new_movie_info.getEnable():
            new_movie_info.setEnable(True)

        if new_movie_info != self.current_movie_info:
            if self.current_movie_info is not None:
                new_movie_info.setAlpha(self.current_movie_info.getAlpha())
                self.current_movie_info.setEnable(False)

            self.current_movie_info = new_movie_info

    def __scopeShowInfoAlphaIn(self, source):
        self.__updateCurrentInfoMovie()

        movie_info = self.current_movie_info
        en_movie_info = movie_info.getEntityNode()

        if not movie_info.getEnable():
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaIn(): self.current_movie_info.getEnable() == False")
            return

        if en_movie_info is None:
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaIn(): self.current_movie_info.getEnityNode() is None")
            return

        if not en_movie_info.isActivate():
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaIn(): self.current_movie_info.getEnityNode() !isActivate()")
            return

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addTask("TaskNodeAlphaTo", Node=en_movie_info, Interrupt=True, To=1.0, Time=AmuletPowerButton.HINT_TEXT_ALPHA_TIME)
            parallel_2.addPlay(movie_info, Loop=True, Wait=False)

    def __scopeShowInfoAlphaOut(self, source):
        movie_info = self.current_movie_info
        en_movie_info = movie_info.getEntityNode()

        if not movie_info.getEnable():
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaOut(): self.current_movie_info.getEnable() == False")
            return

        if en_movie_info is None:
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaOut(): self.getInfoMovie().getEnityNode() is None")
            return

        if not en_movie_info.isActivate():
            Trace.log("Entity", 0, "AmuletPowerButton::scopeShowInfoAlphaOut(): self.getInfoMovie().getEnityNode() !isActivate()")
            return

        source.addTask("TaskNodeAlphaTo", Node=en_movie_info, Interrupt=True, To=0.0, Time=AmuletPowerButton.HINT_TEXT_ALPHA_TIME)
        source.addTask("TaskMovie2Stop", Movie2=movie_info)

    def __runTCShowInfoAlphaIn(self):
        if self.__tc_show_info_alpha_in is not None:
            return

        self.__tc_show_info_alpha_in = TaskManager.createTaskChain()

        with self.__tc_show_info_alpha_in as tc:
            tc.addScope(self.__scopeShowInfoAlphaIn)

    def __runTCShowInfoAlphaOut(self):
        if self.__tc_show_info_alpha_out is not None:
            return

        self.__tc_show_info_alpha_out = TaskManager.createTaskChain()

        with self.__tc_show_info_alpha_out as tc:
            tc.addScope(self.__scopeShowInfoAlphaOut)

    def __cancelTCShowInfoAlphaIn(self):
        if self.__tc_show_info_alpha_in is not None:
            self.__tc_show_info_alpha_in.cancel()
            self.__tc_show_info_alpha_in = None

    def __cancelTCShowInfoAlphaOut(self):
        if self.__tc_show_info_alpha_out is not None:
            self.__tc_show_info_alpha_out.cancel()
            self.__tc_show_info_alpha_out = None

    def __restoreInfoMovies(self):
        for movie in self.movies_info.values():
            movie.setAlpha(0.0)
            movie.setEnable(False)

    def enableShowInfoOnCursorHandler(self):
        self.b_show_info_on_cursor_enabled = True

        if self.__tc_show_info_handler is not None:
            return

        self.__tc_show_info_handler = TaskManager.createTaskChain(Repeat=True)

        with self.__tc_show_info_handler as tc:
            tc.addScope(self.__scopeDynamicCurrentMovieSocketTask, "TaskMovie2SocketEnter")
            tc.addFunction(self.__cancelTCShowInfoAlphaOut)
            tc.addFunction(self.__runTCShowInfoAlphaIn)
            tc.addScope(self.__scopeDynamicCurrentMovieSocketTask, "TaskMovie2SocketLeave")
            tc.addFunction(self.__cancelTCShowInfoAlphaIn)
            tc.addFunction(self.__runTCShowInfoAlphaOut)

    def disableShowInfoOnCursorHandler(self):
        self.b_show_info_on_cursor_enabled = False
        self.b_show_info_on_timer_active = False

        if self.__tc_show_info_handler is not None:
            self.__tc_show_info_handler.cancel()
            self.__tc_show_info_handler = None

        self.__cancelTCShowInfoAlphaIn()
        self.__cancelTCShowInfoAlphaOut()

        self.__restoreInfoMovies()

    def showInfoOnTimerHandler(self):
        if self.b_show_info_on_timer_active:
            return

        self.b_show_info_on_timer_active = True

        if self.b_show_info_on_cursor_enabled:
            if self.__tc_show_info_handler is not None:
                self.__tc_show_info_handler.cancel()
                self.__tc_show_info_handler = None

            self.__cancelTCShowInfoAlphaIn()
            self.__cancelTCShowInfoAlphaOut()

        def cb(*_, **__):
            self.__tc_show_info_handler = None

            if self.b_show_info_on_cursor_enabled:
                self.enableShowInfoOnCursorHandler()

            self.b_show_info_on_timer_active = False

        self.__tc_show_info_handler = TaskManager.createTaskChain(Cb=cb)

        with self.__tc_show_info_handler as tc:
            tc.addFunction(self.__cancelTCShowInfoAlphaOut)
            tc.addFunction(self.__runTCShowInfoAlphaIn)
            tc.addDelay(self.HINT_TEXT_SHOW_TIME)
            tc.addFunction(self.__cancelTCShowInfoAlphaIn)
            tc.addFunction(self.__runTCShowInfoAlphaOut)

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def cleanUp(self):
        self.disableShowInfoOnCursorHandler()

        for obj_movie in self.movies.values():
            obj_movie.onDestroy()

    def getLocked(self):
        state = self.sys_spell_amulet_stone.getLocked()
        return state

class Amulet(object):
    IDLE = 'idle'
    HIDE = 'hide'
    OPEN = 'open'

    # deprecated: EVENT_AMULET_STATE_CHANGE = Event('SpellAmuletStateChange')
    NOTIFICATOR_AmuletStateChange = Notificator.onSpellAmuletStateChange

    SEMAPHORE_APPEAR_AMULET = Semaphore(False, 'SpellAmuletAppearAmulet')

    def __init__(self, movie_idle, movie_hide, movie_open, button_hint):
        self.movies_amulet_states = {Amulet.IDLE: movie_idle, Amulet.HIDE: movie_hide, Amulet.OPEN: movie_open}

        self.button_hint = button_hint
        button_hint.setEnable(False)

        self.power_buttons = dict()

        for obj_movie in self.movies_amulet_states.values():
            obj_movie.setEnable(False)

        movie_hide.setEnable(True)
        movie_hide.setLastFrame(True)
        self.cur_amulet_movie = movie_hide
        self.cur_amulet_state = Amulet.HIDE

        self.button_hint_appear_time = movie_open.entity.getDuration()
        self.button_hint_disappear_time = movie_hide.entity.getDuration()

        self.__tcs = []

    def addPowerButton(self, power_type, power_button):
        self.power_buttons[power_type] = power_button

    def addButtonToCurMovieStateSlot(self, slot_name, *movie_objs):
        slot = self.cur_amulet_movie.getMovieSlot(slot_name)

        for movie_obj in movie_objs:
            movie_en = movie_obj.getEntityNode()
            slot.addChild(movie_en)

    def getCurState(self):
        return self.cur_amulet_state

    def getCurMovie(self):
        return self.cur_amulet_movie

    def scopeClick(self, source, target):
        movie = self.cur_amulet_movie
        if movie.hasSocket(target):
            source.addTask("TaskMovie2SocketClick", Movie2=movie, SocketName=target)
        else:
            source.addDummy()
            Trace.log("Entity", 0, "Wrong target name {!r} in amulet {!r}".format(target, movie.getName()))

    def isOpen(self, in_idle=False):
        if in_idle is True:
            b_open = self.cur_amulet_state == Amulet.IDLE
        else:
            b_open = self.cur_amulet_state != Amulet.HIDE
        return b_open

    # MOVIE STATES BLOCK ///////////////////////////////////////////////////////////////////////////////////////////////
    def changeState(self, state, play=None, loop=None, last_frame=None):
        self.cur_amulet_movie.setEnable(False)

        new_cur_movie = self.movies_amulet_states[state]
        new_cur_movie.setEnable(True)

        if play is not None:
            new_cur_movie.setPlay(play)
        if loop is not None:
            new_cur_movie.setLoop(loop)
        if last_frame is not None:
            new_cur_movie.setLastFrame(last_frame)

        self.cur_amulet_movie = new_cur_movie
        self.cur_amulet_state = state

        for power_button in self.power_buttons.values():
            power_button.attachMoviesToAmuletObjCurStateMovie()

        Notification.notify(Amulet.NOTIFICATOR_AmuletStateChange, state)

    def scopePlayCurState(self, source, **params):
        source.addPlay(self.cur_amulet_movie, **params)

    def setEnableCurrentAmuletMovie(self, enable):
        """
        When we play Amulet_Use we play movie from AmuletPowerButton
        it's not state of the Amulet, when we do that we call this method
        to temporary hide amulet
        """
        self.cur_amulet_movie.setEnable(enable)

    def scopeOpenAmulet(self, source):
        if self.cur_amulet_state is not Amulet.HIDE:
            source.addDummy()
            return

        source.addFunction(self.changeState, Amulet.OPEN, play=False, last_frame=False)
        source.addScope(self.scopePlayCurState)

        source.addFunction(self.changeState, Amulet.IDLE, play=True, loop=True)
        source.addNotify(Amulet.NOTIFICATOR_AmuletStateChange, self.OPEN)
        source.addFunction(self.enableShowInfoTCs, True)
        source.addNotify(Notificator.onSpellAmuletOpenClose, True)

    def scopeCloseAmulet(self, source, skip_play=False):
        if self.cur_amulet_state is Amulet.HIDE:
            source.addDummy()
            return

        spell_ui_component = SystemSpells.getSpellUIComponent('amulet')
        spell_amulet_demon = spell_ui_component.getSpellDemon()
        quests = spell_ui_component.getSceneActiveQuests()

        for quest in quests:
            power_name = quest.params["PowerName"]
            spell_amulet_power = SystemSpells.getSpellAmuletStoneByPower(power_name)
            power_type = spell_amulet_power.param.power_type
            spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(power_type)

            if spell_amulet_button.getLocked() is False:
                source.addFunction(spell_amulet_button.changeState, spell_amulet_button.IDLE, play=True, loop=True)

        source.addFunction(self.enableShowInfoTCs, False)
        source.addFunction(self.changeState, Amulet.HIDE, play=False, last_frame=skip_play)

        if not skip_play:
            source.addScope(self.scopePlayCurState)

        source.addNotify(Notificator.onSpellAmuletOpenClose, False)

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # TC BLOCK /////////////////////////////////////////////////////////////////////////////////////////////////////////
    def enableShowInfoTCs(self, enable):
        if enable:
            for power_button in self.power_buttons.values():
                power_button.enableShowInfoOnCursorHandler()
        else:
            for power_button in self.power_buttons.values():
                power_button.disableShowInfoOnCursorHandler()

    def showInfo_OnHintButton(self):
        if self.cur_amulet_state == Amulet.IDLE:
            for power_button in self.power_buttons.values():
                power_button.showInfoOnTimerHandler()

    def enableTCs(self):
        self.button_hint.setAlpha(0.0)
        en_button_hint = self.button_hint.getEntityNode()

        self.SEMAPHORE_APPEAR_AMULET.setValue(False)

        # RESOLVE BUTTON_HINT APPEARING
        tc_power_hint_button_appear = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_power_hint_button_appear)

        with tc_power_hint_button_appear as tc:
            tc.addListener(self.NOTIFICATOR_AmuletStateChange, lambda state: state is self.OPEN)
            tc.addSemaphore(self.SEMAPHORE_APPEAR_AMULET, From=False)

            with tc.addRaceTask(2) as (race_interrupt, race_enter):
                race_interrupt.addListener(self.NOTIFICATOR_AmuletStateChange, lambda state: state in [self.HIDE, AmuletPowerButton.AIM])

                race_enter.addFunction(self.disableAmuletHintButton, False)
                race_enter.addEnable(self.button_hint)
                race_enter.addTask("TaskNodeAlphaTo", Node=en_button_hint, To=1.0, Time=self.button_hint_appear_time, Interrupt=True)

            tc.addSemaphore(self.SEMAPHORE_APPEAR_AMULET, To=True)

        # RESOLVE BUTTON_HINT DISAPPEARING
        tc_power_hint_button_disappear = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_power_hint_button_disappear)

        with tc_power_hint_button_disappear as tc:
            tc.addListener(self.NOTIFICATOR_AmuletStateChange, lambda state: state is self.HIDE)
            tc.addSemaphore(self.SEMAPHORE_APPEAR_AMULET, From=True)

            with tc.addRaceTask(2) as (race_interrupt, race_leave):
                race_interrupt.addListener(self.NOTIFICATOR_AmuletStateChange, lambda state: state in [self.OPEN, AmuletPowerButton.AIM])

                race_leave.addFunction(self.disableAmuletHintButton, True)
                race_leave.addEnable(self.button_hint)
                race_leave.addTask("TaskNodeAlphaTo", Node=en_button_hint, To=0.0, Time=self.button_hint_disappear_time, Interrupt=True)

                race_leave.addDisable(self.button_hint)
                race_leave.addFunction(self.disableAmuletHintButton, True)

            tc.addSemaphore(self.SEMAPHORE_APPEAR_AMULET, To=False)
        #

        # RESOLVE BUTTON_HINT HIDE ON USE
        tc_power_hint_button_hide_on_aim = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_power_hint_button_hide_on_aim)

        with tc_power_hint_button_hide_on_aim as tc:
            tc.addListener(self.NOTIFICATOR_AmuletStateChange, lambda state: state is AmuletPowerButton.AIM)
            tc.addDisable(self.button_hint)
            tc.addFunction(self.button_hint.setAlpha, 0.0)
            tc.addFunction(self.disableAmuletHintButton, True)
        #

        # RESOLVE BUTTON_HINT PRESSED
        tc_power_hint_button_show_hint = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_power_hint_button_show_hint)

        with tc_power_hint_button_show_hint as tc:
            tc.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_hint)
            tc.addFunction(self.showInfo_OnHintButton)  #

    def disableTCs(self):
        for tc in self.__tcs:
            tc.cancel()
        self.__tcs = []

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def disableAmuletHintButton(self, state):
        self.button_hint.setBlock(state)

    def cleanUp(self):
        self.disableTCs()

class SpellAmulet(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def __init__(self):
        super(SpellAmulet, self).__init__()
        self.amulet = None
        self.amulet_power_buttons = dict()

        self.__tc = None

    def getAmulet(self):
        return self.amulet

    def getSpellAmuletButton(self, power_type):
        return self.amulet_power_buttons.get(power_type)

    def getSpellAmuletButtonByPower(self, power_name):
        stone = SystemSpells.getSpellAmuletStoneByPower(power_name)
        power_type = stone.param.power_type
        return self.amulet_power_buttons.get(power_type)

    def __runTaskChain(self):
        """
        # NOTIFY SYSTEM SPELLS THAT BUTTON CLICKED
        # ENABLE AMULET_HINT_BUTTON_TC's
        """

        if DefaultManager.getDefaultBool("SpellAmuletEnableHint", False) is True:
            self.amulet.enableTCs()
        else:
            self.amulet.button_hint.setEnable(False)

        self.__tc = TaskManager.createTaskChain(Repeat=True)
        with self.__tc as tc:
            tc.addFunction(CursorManager.setCursorMode, "Default")
            for (power_type, power_button_obj), race in tc.addRaceTaskList(self.amulet_power_buttons.iteritems()):
                with race.addRaceTask(2) as (click, arrow):
                    click.addScope(power_button_obj.scopeClick)
                    click.addNotify(Notificator.onSpellAmuletButtonClick, power_type, power_button_obj.cur_button_state)

                    # Here we change cursor for every spell stone
                    with arrow.addIfTask(power_button_obj.getLocked) as (wait_unlock, change):
                        wait_unlock.addListener(Notificator.onSpellAmuletAddPower, Filter=power_button_obj.unlockFilter)
                        change.addScope(power_button_obj.scopeChangeCursorMode)

        tc_close = TaskManager.createTaskChain(Name="SpellAmuletClose", Repeat=True)
        with tc_close as tc:
            with tc.addRaceTask(2) as (idle, interrupt):
                with idle.addIfTask(self.amulet.isOpen, True) as (true, false):
                    true.addDummy()
                    false.addListener(self.amulet.NOTIFICATOR_AmuletStateChange, lambda state: state == self.amulet.IDLE)

                idle.addScope(self.amulet.scopeClick, "close")
                with GuardBlockInput(idle) as guard_parallel_1:
                    guard_parallel_1.addScope(self.amulet.scopeCloseAmulet)

                interrupt.addListener(self.amulet.NOTIFICATOR_AmuletStateChange, lambda state: state != self.amulet.HIDE)

    def __cleanUp(self):
        if self.__tc is not None:
            self.__tc.cancel()
            self.__tc = None

        if TaskManager.existTaskChain("SpellAmuletClose") is True:
            TaskManager.cancelTaskChain("SpellAmuletClose")

        self.amulet.cleanUp()

        for power_button in self.amulet_power_buttons.values():
            power_button.cleanUp()

        self.amulet_power_buttons = {}

    def _onPreparation(self):
        amulet_param = SpellsManager.getSpellAmuletParam()
        obj_getter = self.object.getObject

        amulet_idle_movie = obj_getter(amulet_param.movie2_amulet_idle)
        amulet_hide_movie = obj_getter(amulet_param.movie2_amulet_hide)
        amulet_open_movie = obj_getter(amulet_param.movie2_amulet_open)
        amulet_hint = obj_getter(amulet_param.movie2button_amulet_hint)

        self.amulet = Amulet(amulet_idle_movie, amulet_hide_movie, amulet_open_movie, amulet_hint)
        AmuletPowerButton.AMULET = self.amulet
        AmuletPowerButton.SPELL_AMULET_OBJECT = self.object

        AmuletPowerButton.SOCKET_NAME = amulet_param.socket_name
        AmuletPowerButton.ALIAS_POWER_DESC = amulet_param.text_alias_power_description
        AmuletPowerButton.ALIAS_POWER_LOCKED = amulet_param.text_alias_power_locked
        AmuletPowerButton.HINT_TEXT_ALPHA_TIME = amulet_param.hint_text_alpha_time
        AmuletPowerButton.HINT_TEXT_SHOW_TIME = amulet_param.hint_text_show_time
        AmuletPowerButton.AMULET_USE_ALPHA_TIME = amulet_param.amulet_use_alpha_time

        sys_spell_amulet_stones = SystemSpells.getSpellAmuletStones()
        for power_type, sys_spell_amulet_stone in sys_spell_amulet_stones.items():
            self.amulet_power_buttons[power_type] = AmuletPowerButton(sys_spell_amulet_stone)

    def _onActivate(self):
        self.__runTaskChain()

    def _onDeactivate(self):
        self.__cleanUp()