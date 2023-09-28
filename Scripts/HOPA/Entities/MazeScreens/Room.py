from Foundation.Initializer import Initializer
from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSObject
from HOPA.Entities.MazeScreens.Gate import Gate
from HOPA.Entities.MazeScreens.Lever import Lever
from HOPA.Entities.MazeScreens.Transition import Transition
from HOPA.System.SystemNavigation import SystemNavigation


class Room(Initializer):

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
        self.game.object.addChild(root)
        self.root = root

        content_movie = self.game.object.generateObject("Content", self.params.content_name)
        content_movie.setLoop(True)
        content_movie.setPlay(True)
        root.addChild(content_movie.getEntityNode())
        self.content_movie = content_movie

        for params in MazeScreensManager.getContentSlots(self.game.EnigmaName, self.params.content_name):
            slot = content_movie.getMovieSlot(params.name)
            obj = self._generateObject(slot, params)
            self._objects.append(obj)

        self.setEnable(False)

    def onActivate(self):
        if self.params.is_start is True:
            self.toggleNavBackButton(False)

        for obj in self._objects:
            obj.onActivate()

    def onDeactivate(self):
        if self.params.is_start is True:
            self.toggleNavBackButton(True)

        for obj in self._objects:
            obj.onDeactivate()

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
        Object.onInitialize(slot, self.game, params)

        return Object

    def setEnable(self, state):
        if self.root is None:
            Trace.log("Enigma", 0, "Room [id {!r}] setEnable: root is None".format(self.id))
            return

        if state is True:
            self.root.enable()
        else:
            self.root.disable()

    def toggleNavBackButton(self, state):
        """ toggle transition back button interactive """
        button = SystemNavigation.getNavGoBackButton()
        button.setInteractive(state)
