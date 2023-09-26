from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSObject
from HOPA.Entities.MazeScreens.Gate import Gate
from HOPA.Entities.MazeScreens.Lever import Lever
from HOPA.Entities.MazeScreens.Transition import Transition


class Room(Initializer):

    def __init__(self):
        super(Room, self).__init__()
        self.id = None
        self.params = None      # RoomParam
        self.__game = None
        self._objects = []
        self.tc = None

        self.root = None
        self.content_movie = None
        self.environment_movie = None

    def _onInitialize(self, game, params):
        self.__game = game
        self.params = params
        self.id = params.id

    def onPreparation(self):
        root = Mengine.createNode("Interender")
        root.setName("Room_{}".format(self.id))
        self.root = root

        environment_movie = self.__game.object.generateObject("Environment", self.params.environment_name)
        root.addChild(environment_movie)
        self.environment_movie = environment_movie

        content_slots_movie = self.__game.object.generateObject("ContentSlots", self.params.content_name)
        root.addChild(content_slots_movie)
        self.content_movie = content_slots_movie

        for params in MazeScreensManager.getContentSlots(self.__game.EnigmaName, self.params.content_name):
            slot = content_slots_movie.getMovieSlot(params.name)
            obj = self._generateObject(slot, params)
            self._objects.append(obj)

        # todo

    def onActivate(self):
        for obj in self._objects:
            obj.onActivate()
        # todo: activate all objects ?
        self.runTaskChain()

    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="MazeScreensRoom{}Handler".format(self.params.id))
        with self.tc as tc:
            pass

    def onDeactivate(self):
        # todo: deactivate all objects, hide them and wait for next activation
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for obj in self._objects:
            obj.onDeactivate()

    def _onFinalize(self):
        self.onDeactivate()
        for obj in self._objects:
            obj.onFinalize()
        self._objects = []
        # todo: finalize objects

    def _generateObject(self, slot, params):
        movie = self.__game.object.generateObject(params.prototype_name, params.prototype_name)

        Types = {
            MSObject.Lever: Lever,
            MSObject.Gate: Gate,
            MSObject.Transition: Transition,
        }

        Object = Types[params.object_type]()
        Object.onInitialize(movie, params)

        return Object

