from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.CursorManager import CursorManager
from HOPA.MazeScreensManager import MSTransition


class Transition(Initializer):

    def __init__(self):
        super(Transition, self).__init__()
        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.movie = None
        self.tc = None
        self.tc_cursor = None

    def _onInitialize(self, slot, room, params):
        self._params = params
        self.room = room
        self.__slot = slot

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
        if self.tc_cursor is not None:
            self.tc_cursor.cancel()
            self.tc_cursor = None

        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

        self.id = None
        self._params = None
        self.__slot = None
        self.room = None

    def onActivate(self):
        self.movie.setEnable(True)
        self.runTaskChain()

    def onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
        if self.tc_cursor is not None:
            self.tc_cursor.cancel()
            self.tc_cursor = None

        self.movie.setEnable(False)

    def runTaskChain(self):
        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(Name=tc_name)

        with self.tc as tc:
            tc.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="socket")
            tc.addFunction(self.enter)

        tc_cursor_name = tc_name + "_CursorEffect"
        self.tc_cursor = TaskManager.createTaskChain(Name=tc_cursor_name, Repeat=True)

        with self.tc_cursor as tc:
            tc.addTask("TaskMovie2SocketEnter", Movie2=self.movie, SocketName="socket")
            tc.addFunction(self._mouseEnter)

            tc.addTask("TaskMovie2SocketLeave", Movie2=self.movie, SocketName="socket")
            tc.addFunction(self._mouseLeave)

    def enter(self):
        self._mouseLeave()
        self.room.game.movePlayer(self._params.transition_way)

    # cursor handler

    def _mouseEnter(self):
        way = self._params.transition_way
        cursor = self.room.game.params.cursor

        if way == MSTransition.Up:
            cursor_mode = cursor.transition_up
        elif way == MSTransition.Down:
            cursor_mode = cursor.transition_down
        elif way == MSTransition.Left:
            cursor_mode = cursor.transition_left
        elif way == MSTransition.Right:
            cursor_mode = cursor.transition_right
        else:
            cursor_mode = cursor.transition_up

        CursorManager._arrowEnterFilter(self.movie, cursor_mode)
        # CursorManager.setCursorMode(cursor_mode, True)

    def _mouseLeave(self):
        CursorManager._arrowLeaveFilter(self.movie)
