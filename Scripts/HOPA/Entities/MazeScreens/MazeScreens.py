from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.Entities.MazeScreens.Room import Room


Enigma = Mengine.importEntity("Enigma")


class MazeScreens(Enigma):

    def __init__(self):
        super(MazeScreens, self).__init__()
        self.tc = None
        self.params = None
        self._rooms = {}    # {room_id: Room}

    def _onPreparation(self):
        self._prepare()

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        self._cleanFull()

    def _playEnigma(self):
        pass # task chains

    def _skipEnigma(self):
        self._cleanFull()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._cleanFull()
        self._prepare()
        self._playEnigma()

    def _prepare(self):
        self.params = MazeScreensManager.getSettings(self.EnigmaName)
        self._setup()

    def _cleanFull(self):
        pass

    def _setup(self):
        for room_params in self.params.rooms:
            room = Room()
            room.onInitialize(room_params)

            self._rooms[room_params.id] = room
