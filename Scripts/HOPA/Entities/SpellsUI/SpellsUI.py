from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.SpellsManager import SpellsManager
from HOPA.System.SystemSpells import SystemSpells
from Notification import Notification


def OBJECTS_IS_ACTIVE(object_list):
    for obj in object_list:
        if not obj.isActive():
            return False
    return True


class SpellRune(object):
    READY = 'ready'
    IDLE = 'idle'
    APPEAR = 'appear'

    def __init__(self, sys_spells_ui_rune, SPELLS_UI_OBJECT):
        self.SPELLS_UI_OBJECT = SPELLS_UI_OBJECT
        self.sys_spells_ui_rune = sys_spells_ui_rune
        spell_ui_rune_param = sys_spells_ui_rune.params

        self.rune_type = spell_ui_rune_param.rune_type

        self.movies = {
            SpellRune.READY: self.SPELLS_UI_OBJECT.getObject(spell_ui_rune_param.movie2_rune_ready),
            SpellRune.IDLE: self.SPELLS_UI_OBJECT.getObject(spell_ui_rune_param.movie2_rune_idle),
            SpellRune.APPEAR: self.SPELLS_UI_OBJECT.getObject(spell_ui_rune_param.movie2_rune_appear)
        }

        for obj_movie in self.movies.values():
            obj_movie.setEnable(False)
            obj_movie.setPlay(False)

    def getRuneType(self):
        return self.rune_type


class SpellButton(object):
    SPELLS_UI_SLOTS_MOVIE = None
    SPELLS_UI_OBJECT = None

    # resolved from SystemSpells and onPreparation
    READY = 'ready'
    IDLE = 'idle'
    LOCKED = 'locked'

    # resolved from SystemSpells
    USE = 'use'
    UPDATE = 'update'

    # deprecated: EVENT_STATE_UPDATE = Event('SpellButton_MovieStateUpdate_Event')
    NOTIFICATOR_ButtonStateChange = Notificator.onSpellAmuletSpellButtonStateChange

    SOCKET_NAME = 'socket'

    @classmethod
    def addButtonToSlot(cls, slot_name, obj_movie2):
        movie2_en = obj_movie2.getEntityNode()
        slot = cls.SPELLS_UI_SLOTS_MOVIE.getMovieSlot(slot_name)
        slot.addChild(movie2_en)

    def __init__(self, sys_spells_ui_component):
        self.spell_runes = dict()
        self.sys_spells_ui_component = sys_spells_ui_component

        spell_ui_button_param = sys_spells_ui_component.param_ui_button

        self.spell_type = spell_ui_button_param.spell_type

        self.movies = {
            SpellButton.READY: self.SPELLS_UI_OBJECT.getObject(spell_ui_button_param.movie2_spell_button_ready),
            SpellButton.IDLE: self.SPELLS_UI_OBJECT.getObject(spell_ui_button_param.movie2_spell_button_idle),
            SpellButton.USE: self.SPELLS_UI_OBJECT.getObject(spell_ui_button_param.movie2_spell_button_use),
            SpellButton.LOCKED: self.SPELLS_UI_OBJECT.getObject(spell_ui_button_param.movie2_spell_button_locked),
            SpellButton.UPDATE: self.SPELLS_UI_OBJECT.getObject(spell_ui_button_param.movie2_spell_button_update)
        }

        sys_spells_ui_runes = SystemSpells.getSpellUIRunes()

        for rune_type, sys_spells_ui_rune in sys_spells_ui_runes.items():
            rune = SpellRune(sys_spells_ui_rune, self.SPELLS_UI_OBJECT)
            self.spell_runes[rune_type] = rune

        slot_name = spell_ui_button_param.slot_name
        for obj_movie in self.movies.values():
            SpellButton.addButtonToSlot(slot_name, obj_movie)
            obj_movie.setEnable(False)
            obj_movie.setPlay(False)

        self.cur_movie = self.movies[SpellButton.LOCKED]
        self.cur_state = self.getStateUpdate()

        play_and_loop = self.cur_state in [SpellButton.IDLE, SpellButton.READY]
        self.changeState(self.cur_state, play_and_loop, play_and_loop)

    # MOVIE STATES BLOCK ///////////////////////////////////////////////////////////////////////////////////////////////
    def changeState(self, state, play=None, loop=None, last_frame=None):
        # print("SpellUI Change state, state is {}".format(state))
        new_cur_movie = self.movies[state]
        found_runes = SystemSpells.s_spell_ui_runes_settings.found_runes
        runes_settings = SystemSpells.s_spell_ui_runes_settings
        rune_to_use = SystemSpells.s_spell_ui_runes_settings.getRuneToUse()
        # check:
        add_new_rune = False
        if not OBJECTS_IS_ACTIVE([self.SPELLS_UI_OBJECT, self.cur_movie, new_cur_movie]):
            return

        self.cur_movie.setEnable(False)
        new_cur_movie.setEnable(True)

        if len(found_runes) is not 0 and runes_settings.getReady() is not False:
            add_new_rune = True
            for rune in found_runes:
                if rune is found_runes[-1]:
                    self.spell_runes[rune].movies["appear"].setEnable(True)
                    self.spell_runes[rune].movies["appear"].setPlay(True)
                else:
                    self.spell_runes[rune].movies["idle"].setEnable(True)
            runes_settings.setReady(False)

        if len(found_runes) is not 0 and add_new_rune is False:
            if state is "ready":
                rune_state = state
            else:
                rune_state = "idle"

            if len(found_runes) is not 0 and rune_state is "idle":
                for rune in found_runes:
                    self.spell_runes[rune].movies[rune_state].setEnable(True)

            if rune_to_use is not None and rune_state is "ready":
                for rune in found_runes:
                    if rune == rune_to_use:
                        self.spell_runes[rune].movies[rune_state].setEnable(True)
                    else:
                        self.spell_runes[rune].movies["idle"].setEnable(True)

        if play is not None:
            new_cur_movie.setPlay(play)
            self.playLoopReloadRune("play", found_runes, state, play)
        if loop is not None:
            new_cur_movie.setLoop(loop)
            self.playLoopReloadRune("loop", found_runes, state, loop)
        if last_frame is not None:
            new_cur_movie.setLastFrame(last_frame)
            self.playLoopReloadRune("reload", found_runes, state, last_frame)

        self.cur_movie = new_cur_movie
        self.cur_state = state
        Notification.notify(SpellButton.NOTIFICATOR_ButtonStateChange, self, state)

    def playLoopReloadRune(self, task, found_runes, state, play_loop):
        if len(found_runes) is not 0:
            for rune in found_runes:
                if task == "play":
                    self.spell_runes[rune].movies[state].setPlay(play_loop)
                elif task == "loop":
                    self.spell_runes[rune].movies[state].setLoop(play_loop)
                elif task == "reload":
                    self.spell_runes[rune].movies[state].setLastFrame(play_loop)

    def getStateUpdate(self):
        """
        Try to get correct movie state from System param etc.
        :return: movie state key from self.movies dict
        """
        if self.sys_spells_ui_component.getLocked():
            return SpellButton.LOCKED
        elif self.sys_spells_ui_component.hasSceneActiveQuest():
            return SpellButton.READY
        else:
            return SpellButton.IDLE

    def disableAllStatesMovies(self):
        # print("Disable all movies")
        """
        If we call update when another update is executing,
        we need to clear update execution result
        """
        movies = self.movies.values()
        runes = self.spell_runes.values()

        # check
        if not OBJECTS_IS_ACTIVE([self.SPELLS_UI_OBJECT] + movies):
            return

        for rune in runes:
            movies_runes = rune.movies.values()
            for movie in movies_runes:
                movie.setEnable(False)

        for obj_movie in movies:
            obj_movie.setEnable(False)

    def scopePlayCurState(self, source, **params):
        # check

        if not OBJECTS_IS_ACTIVE([self.SPELLS_UI_OBJECT, self.cur_movie]):
            return

        source.addPlay(self.cur_movie, **params)

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def __scopeTaskMovie2SocketClick(self, source, semaphore):
        source.addTask('TaskMovie2ButtonClick', DemonName='SpellsUI', Movie2ButtonName='Movie2Button_Amulet_FFG')
        source.addSemaphore(semaphore, To=True)

    def scopeClickCurMovieSocket(self, source):
        """
        Dynamic TaskMovie2SocketClick, when state updated, new socket clicked task is appeared
        """
        semaphore = Semaphore(False, self.spell_type)

        with source.addRepeatTask() as (repeat, until):
            with repeat.addRaceTask(2) as (race_0, race_1):
                race_0.addListener(SpellButton.NOTIFICATOR_ButtonStateChange, lambda obj, state: obj is self)
                race_1.addScope(self.__scopeTaskMovie2SocketClick, semaphore)

            until.addSemaphore(semaphore, From=True)

        source.addNotify(Notificator.onSpellUISpellButtonClick, self.spell_type, self.cur_state)

    def cleanUp(self):
        for obj_movie in self.movies.values():
            self.SPELLS_UI_OBJECT.getEntityNode().addChild(obj_movie.getEntityNode())


class SpellsUI(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def __init__(self):
        super(SpellsUI, self).__init__()
        self.spell_buttons = dict()

        self.__tc = None

    def getSpellUIButton(self, spell_type):
        return self.spell_buttons.get(spell_type)

    def __runTaskChain(self):
        """
        # NOTIFY SYSTEM SPELLS THAT BUTTON CLICKED
        """
        self.__tc = TaskManager.createTaskChain(Repeat=True)

        with self.__tc as tc:
            for (spell_type, spell_button), race in tc.addRaceTaskList(self.spell_buttons.iteritems()):
                race.addScope(spell_button.scopeClickCurMovieSocket)

    def __cleanUp(self):
        if self.__tc is not None:
            self.__tc.cancel()
            self.__tc = None

        for spell_button in self.spell_buttons.values():
            spell_button.cleanUp()

        self.spell_buttons = {}

    def _onPreparation(self):
        super(SpellsUI, self)._onPreparation()

        spells_ui_param = SpellsManager.getSpellsUIParam()

        SpellButton.SPELLS_UI_SLOTS_MOVIE = self.object.getObject(spells_ui_param.movie2_spell_slots)
        SpellButton.SPELLS_UI_OBJECT = self.object
        SpellButton.SOCKET_NAME = spells_ui_param.socket_name

        sys_spells_ui_components = SystemSpells.getSpellUIComponents()

        for spell_type, sys_spells_ui_component in sys_spells_ui_components.items():
            spell_button = SpellButton(sys_spells_ui_component)
            self.spell_buttons[spell_type] = spell_button

    def _onActivate(self):
        super(SpellsUI, self)._onActivate()
        self.__runTaskChain()

    def _onPreparationDeactivate(self):
        super(SpellsUI, self)._onPreparationDeactivate()
        self.__cleanUp()
