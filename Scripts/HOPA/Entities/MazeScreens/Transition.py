from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager

# todo: add arrow enter\leave effect depending on way (up, down, right, left)


class Transition(Initializer):

    def __init__(self):
        super(Transition, self).__init__()
        self.id = None
        self._params = None
        self.__slot = None
        self.room = None
        self.movie = None
        self.tc = None

    def _onInitialize(self, slot, room, params):
        self._params = params
        self.room = room
        self.__slot = slot

        self.id = "{}_{}_{}".format("Transition", self.room.id, self.__slot.getName())

        prototype_name = self._params.prototype_name
        movie_name = self._params.prototype_name

        movie_params = dict(Interactive=True, Enable=False, Play=False, Loop=False)
        movie = room.game.object.generateObject(movie_name, prototype_name, movie_params)

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

    def onActivate(self):
        self.runTaskChain()

    def onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.movie.setEnable(False)

    def runTaskChain(self):
        tc_name = "MazeScreens_{}".format(self.id)
        self.tc = TaskManager.createTaskChain(tc_name)

        with self.tc as tc:
            tc.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="socket")
            tc.addFunction(self.enter)

    def enter(self):
        self.room.game.movePlayer(self._params.transition_way)

