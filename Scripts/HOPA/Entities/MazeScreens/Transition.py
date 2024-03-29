from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.CursorManager import CursorManager


class Transition(Initializer):

    def __init__(self):
        super(Transition, self).__init__()
        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.movie = None
        self.tc = None
        self.EventClick = None

    def _onInitialize(self, slot, room, params):
        self._params = params
        self.room = room
        self.__slot = slot
        self.EventClick = Event("onClick")

        self.id = "{}_{}_{}".format("Transition", self.room.id, self.__slot.getName())

        prototype_name = self._params.prototype_name
        movie_name = self._params.prototype_name

        movie_params = dict(Interactive=True, Enable=False, Play=False, Loop=False)
        movie = room.game.object.generateObjectUnique(movie_name, prototype_name, **movie_params)

        slot.addChild(movie.getEntityNode())
        self.movie = movie

    def _onFinalize(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.EventClick = None

    def onActivate(self):
        self.movie.setEnable(True)
        self.runTaskChain()

    def onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.movie.setEnable(False)

    def runTaskChain(self):
        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(Name=tc_name)

        with self.tc as tc:
            with tc.addRaceTask(2) as (tc_enter, tc_cursor):
                tc_enter.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="socket")
                tc_enter.addFunction(self.enter)

                # this source works until scene enter
                tc_cursor.addScope(self._scopeCursorHandler, self.movie, self._params.cursor_mode)

    def enter(self):
        self.room.game.movePlayer(self._params.transition_way)

    # cursor handler

    def _scopeCursorHandler(self, source, Movie, cursor_mode):
        with source.addRepeatTask() as (source_repeat, source_until):
            source_repeat.addTask("TaskMovie2SocketEnter", Movie2=Movie, SocketName="socket")
            source_repeat.addFunction(self._mouseEnter, self, cursor_mode)

            source_repeat.addTask("TaskMovie2SocketLeave", Movie2=Movie, SocketName="socket")
            source_repeat.addFunction(self._mouseLeave, self)

            source_until.addEvent(self.EventClick)

    def _mouseEnter(self, Movie, cursor_mode):
        CursorManager._arrowEnterFilter(Movie, cursor_mode)

    def _mouseLeave(self, Movie):
        CursorManager._arrowLeaveFilter(Movie)
