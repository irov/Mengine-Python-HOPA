from Foundation.Initializer import Initializer
from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSObject
from HOPA.Entities.MazeScreens.Gate import Gate
from HOPA.Entities.MazeScreens.Lever import Lever
from HOPA.Entities.MazeScreens.Transition import Transition


class Room(Initializer):

    def __repr__(self):
        return str(self.id)

    def __init__(self):
        super(Room, self).__init__()
        self.id = None
        self.params = None      # RoomParam
        self.game = None        # MazeScreens entity
        self._objects = []

        self.root = None
        self.content_movie = None

    def _onInitialize(self, game, params):
        self.game = game
        self.params = params
        self.id = params.id

    def onPreparation(self):
        root = Mengine.createNode("Interender")
        root.setName("Room_{}".format(self.id))
        self.game.addChild(root)
        self.root = root

        content_params = dict(Enable=True, Loop=True, Play=True)
        content_name = MazeScreensManager.getContentName(self.game.EnigmaName, self.params.content_id)
        content_movie = self.game.object.generateObjectUnique("Content", content_name, **content_params)
        root.addChild(content_movie.getEntityNode())
        self.content_movie = content_movie

        for params in MazeScreensManager.getContentSlots(self.game.EnigmaName, self.params.content_id):
            slot = content_movie.getMovieSlot(params.name)
            obj = self._generateObject(slot, params)
            self._objects.append(obj)

        self.setEnable(False)

    def onActivate(self):
        if self.params.is_start is False:
            self.game.toggleNavBackButton(False)

        for obj in self._objects:
            obj.onActivate()
        self.root.enable()

    def onDeactivate(self):
        if self.params.is_start is False:
            self.game.toggleNavBackButton(True)

        for obj in self._objects:
            obj.onDeactivate()
        self.root.disable()

    def _onFinalize(self):
        for obj in self._objects:
            obj.onFinalize()
        self._objects = []

        if self.content_movie is not None:
            self.content_movie.removeFromParent()
            self.content_movie.onDestroy()
            self.content_movie = None

        if self.root is not None:
            self.root.removeFromParent()
            Mengine.destroyNode(self.root)
            self.root = None

    def _generateObject(self, slot, params):
        Types = {
            MSObject.Lever: Lever,
            MSObject.Gate: Gate,
            MSObject.Transition: Transition,
        }
        Type = Types[params.object_type]

        Object = Type()
        Object.onInitialize(slot, self, params)

        return Object

    def setEnable(self, state):
        if self.root is None:
            Trace.log("Entity", 0, "Room [id {!r}] setEnable: root is None".format(self.id))
            return

        if state is True:
            self.root.enable()
        else:
            self.root.disable()

