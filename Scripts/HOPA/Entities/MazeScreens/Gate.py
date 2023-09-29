from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.TipManager import TipManager


class Gate(Initializer):

    def __init__(self):
        super(Gate, self).__init__()
        self.id = None
        self._params = None     # SlotParam
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

        self.id = "{}_{}_{}".format("Gate", self.room.id, self.__slot.getName())

        for state, movie in self._generateMovies(room.game.object):
            node = movie.getEntityNode()
            slot.addChild(node)
            self.Movies[state] = movie

        self.EventUpdateState = Event("onStateUpdate")
        self.__state = "Close"

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
        if self.room.game.isGroupDone(self._params.group_id) is True:
            self.__state = "Open"

        self.runTaskChain()

    def onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for movie in self.Movies.values():
            movie.setEnable(False)

    def runTaskChain(self):
        Scopes = dict(
            Close=Functor(self.__stateClose, self.Movies.get("Close")),
            Opening=Functor(self.__stateOpening, self.Movies.get("Opening")),
            Open=Functor(self.__stateOpen, self.Movies.get("Open")),
        )

        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(Name=tc_name, Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as tc:
            def __states(isSkip, cb):
                cb(isSkip, self.__state)

            tc.addScopeSwitch(Scopes, __states)

    def __stateClose(self, source, Movie):
        source.addEnable(Movie)

        with source.addRaceTask(2) as (tc_open, tc_tip):
            tc_open.addListener(Notificator.onMazeScreensGroupDone, Filter=lambda g_id: g_id == self._params.group_id)
            tc_open.addFunction(self.setState, "Opening")

            with tc_tip.addRepeatTask() as (tc_tip_repeat, tc_tip_until):
                tc_tip_repeat.addTask("TaskMovie2SocketClick", Movie2=Movie, SocketName="socket")
                tc_tip_repeat.addFunction(TipManager.showTip, "ID_Tip_MazeScreens_GateClosed")
                tc_tip_until.addBlock()

        source.addDisable(Movie)

    def __stateOpening(self, source, Movie):
        if Movie is None:
            source.addFunction(self.setState, "Open")
            return

        source.addEnable(Movie)

        source.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, Loop=False)
        source.addFunction(self.setState, "Open")

        source.addDisable(Movie)

    def __stateOpen(self, source, Movie):
        source.addEnable(Movie)
        # maybe delete all unused states here
        source.addBlock()

    def setState(self, state):
        if state not in self.Movies:
            return
        self.__state = state

    def getState(self):
        return self.__state

    def _generateMovies(self, game_object):
        states = {
            "Close": [self._params.prototype_name + "_Close", True, True],
            "Opening": [self._params.prototype_name + "_Opening", True, False],
            "Open": [self._params.prototype_name + "_Open", True, True],
        }

        for state, (prototype_name, play, loop) in states.items():
            movie_name = "%s_%s" % (prototype_name, state)

            movie_params = dict(Interactive=True, Enable=False, Play=play, Loop=loop)
            movie = game_object.generateObjectUnique(movie_name, prototype_name, **movie_params)

            yield state, movie
