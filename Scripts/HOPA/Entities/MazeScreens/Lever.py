from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.TipManager import TipManager

# todo: add arrow enter\leave effect for state Idle


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
            Idle=Functor(self.__stateIdle, self.Movies.get("Idle")),
            Use=Functor(self.__stateUse, self.Movies.get("Use")),
            Done=Functor(self.__stateDone, self.Movies.get("Done")),
        )

        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(tc_name, Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as tc:
            def __states(isSkip, cb):
                Trace.msg_dev("    {}: run state {}".format(self.id, self.__state))
                cb(isSkip, self.__state)

            tc.addScopeSwitch(Scopes, __states)

    def __stateIdle(self, source, Movie):
        source.addEnable(Movie)

        source.addTask("TaskMovie2SocketClick", Movie2=Movie, SocketName="socket")
        source.addFunction(self.setState, "Use")

        source.addDisable(Movie)

    def __stateUse(self, source, Movie):
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

    def setState(self, state):
        if state not in self.Movies:
            return
        self.__state = state

    def getState(self):
        return self.__state

    def doneGroup(self):
        self.room.game.setGroupDone(self._params.group_id)
        TipManager.showTip("ID_Tip_MazeScreens_LeverUsed")

    def _generateMovies(self, game_object):
        states = {
            "Ready": [self._params.prototype_name + "_Ready", True, True],
            "Use": [self._params.prototype_name + "_Use", True, False],
            "Done": [self._params.prototype_name + "_Done", True, True],
        }

        for state, (prototype_name, play, loop) in states.items():
            movie_name = "%s_%s" % (prototype_name, state)

            movie_params = dict(Interactive=True, Enable=False, Play=play, Loop=loop)
            movie = game_object.generateObject(movie_name, prototype_name, movie_params)

            yield state, movie
