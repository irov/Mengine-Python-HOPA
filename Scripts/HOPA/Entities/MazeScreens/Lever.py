from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.TipManager import TipManager
from HOPA.CursorManager import CursorManager


class Lever(Initializer):

    def __init__(self):
        super(Lever, self).__init__()
        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.Movies = {}
        self.__state = None
        self.EventUpdateState = None
        self.tc = None

    def _onInitialize(self, slot, room, params):
        self._params = params
        self.room = room
        self.__slot = slot

        self.id = "{}_{}_{}".format("Lever", self.room.id, self.__slot.getName())

        for state, movie in self._generateMovies(room.game.object):
            node = movie.getEntityNode()
            slot.addChild(node)
            self.Movies[state] = movie

        self.EventUpdateState = Event("onStateUpdate")
        self.__state = "Idle"

    def _onFinalize(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for movie in self.Movies.values():
            movie.removeFromParent()
            movie.onDestroy()
        self.Movies = {}

        self.EventUpdateState = None
        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.__state = None

    def onActivate(self):
        self.runTaskChain()

    def onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for movie in self.Movies.values():
            movie.setEnable(False)

    def runTaskChain(self):
        Scopes = dict(
            Idle=Functor(self.__stateReady, self.Movies.get("Ready")),
            Use=Functor(self.__stateUse, self.Movies.get("Use")),
            Done=Functor(self.__stateDone, self.Movies.get("Done")),
        )

        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(Name=tc_name, Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as tc:
            def __states(isSkip, cb):
                cb(isSkip, self.__state)

            tc.addScopeSwitch(Scopes, __states)

    # states

    def __stateReady(self, source, Movie):
        cursor_mode = self._params.cursor_mode

        source.addEnable(Movie)

        with source.addRaceTask(2) as (tc_click, tc_cursor):
            tc_click.addTask("TaskMovie2SocketClick", Movie2=Movie, SocketName="socket")
            tc_click.addFunction(self.setState, "Use")

            tc_cursor.addScope(self._scopeCursorHandler, Movie, cursor_mode)

        source.addDisable(Movie)

    def __stateUse(self, source, Movie):
        source.addFunction(self._mouseLeave, self)

        if Movie is None:
            source.addFunction(self.doneGroup)
            source.addFunction(self.setState, "Done")
            return

        source.addEnable(Movie)

        source.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, Loop=False)
        source.addFunction(self.doneGroup)
        source.addFunction(self.setState, "Done")

        source.addDisable(Movie)

    def __stateDone(self, source, Movie):
        source.addEnable(Movie)
        # maybe delete all unused states here
        source.addBlock()

    # cursor handler

    def _scopeCursorHandler(self, source, Movie, cursor_mode):
        with source.addRepeatTask() as (source_repeat, source_until):
            source_repeat.addTask("TaskMovie2SocketEnter", Movie2=Movie, SocketName="socket")
            source_repeat.addFunction(self._mouseEnter, self, cursor_mode)

            source_repeat.addTask("TaskMovie2SocketLeave", Movie2=Movie, SocketName="socket")
            source_repeat.addFunction(self._mouseLeave, self)

            source_until.addEvent(self.EventUpdateState)

    def _mouseEnter(self, Movie, cursor_mode):
        CursorManager._arrowEnterFilter(Movie, cursor_mode)

    def _mouseLeave(self, Movie):
        CursorManager._arrowLeaveFilter(Movie)

    # public

    def setState(self, state):
        if state not in self.Movies:
            return
        self.__state = state

    def getState(self):
        return self.__state

    def doneGroup(self):
        self.room.game.setGroupDone(self._params.group_id)
        TipManager.showTip("ID_Tip_MazeScreens_LeverUsed")

    # utils

    def _generateMovies(self, game_object):
        states = {
            "Ready": [self._params.prototype_name + "_Ready", True, True],
            "Use": [self._params.prototype_name + "_Use", True, False],
            "Done": [self._params.prototype_name + "_Done", True, True],
        }

        for state, (prototype_name, play, loop) in states.items():
            movie_name = "Lever_%s" % state

            movie_params = dict(Interactive=True, Enable=False, Play=play, Loop=loop)
            movie = game_object.generateObjectUnique(movie_name, prototype_name, **movie_params)

            yield state, movie
