from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSTransition
from HOPA.Entities.MazeScreens.Room import Room


Enigma = Mengine.importEntity("Enigma")


class MazeScreens(Enigma):

    # ORM things

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addActionActivate(Type, "CurrentRoom",
                               Update=MazeScreens._updateCurrentRoom)
        Type.addActionActivate(Type, "DoneGroups",
                               Append=MazeScreens._appendDoneGroups)

    def _updateCurrentRoom(self, room_id):
        if room_id is None:
            return
        if room_id not in self._rooms:
            Trace.log("Enigma", 0, "MazeScreens._updateCurrentRoom: not found room %s" % (room_id))
            return

        if self.current_room is not None:
            self.current_room.onDeactivate()

        room = self._rooms[room_id]
        room.onActivate()
        self.current_room = room

        return

    def _appendDoneGroups(self, index, group_id):
        Notification.notify(Notificator.onMazeScreensGroupDone, group_id)

    # entity things

    def __init__(self):
        super(MazeScreens, self).__init__()
        self.params = None
        self._rooms = {}    # {room_id: Room}
        self.current_room = None
        self.board = None
        self.player_position = None

    def _onPreparation(self):
        self._prepare()

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        self._cleanFull()

    # enigma handling

    def _playEnigma(self):
        self.current_room.onActivate()

    def _skipEnigma(self):
        self._complete()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        # todo: show fade
        self._cleanFull()
        self._prepare()
        # todo: hide fade
        self._playEnigma()

    # enigma flow

    def _prepare(self):
        self.params = MazeScreensManager.getSettings(self.EnigmaName)
        self._setupRooms()
        self._setupBoard()

    def _setupRooms(self):
        for room_params in self.params.rooms:
            room = Room()
            room.onInitialize(room_params)
            room.onPreparation()

            self._rooms[room_params.id] = room

    def _setupBoard(self):
        graph = self.params.graph
        self.board = []

        for i in range(graph.width):
            self.board.append([])
            for j in range(graph.height):

                cell = graph.data[i][j]
                if cell == MazeScreensManager.CELL_TYPE_WALL:
                    self.board[i][j] = None
                else:
                    room = self._rooms[cell]
                    self.board[i][j] = room

    def _cleanFull(self):
        for room in self._rooms.values():
            room.onFinalize()
        self._rooms = {}
        self.current_room = None
        self.board = []

        self.params = None

    def setComplete(self):
        self._cleanFull()
        self.enigmaComplete()

    # public methods

    def isGroupDone(self, group_id):
        return group_id in self.DoneGroups

    def setGroupDone(self, group_id):
        self.object.appendParam("DoneGroups", group_id)

    def movePlayer(self, way):
        if way == MSTransition.Win:
            self.setComplete()
            return 

        direction = self.getDirection(way)
        position = (
            self.player_position[0] + direction[0],
            self.player_position[1] + direction[1],
        )
        room = self.board[position[0]][position[1]]

        if room is None:
            Trace.log("Enigma", 0, "MazeScreens impossible to move player {!r} - None on this position {}".format(way, position))
            return

        self.object.setParam("CurrentRoom", room.id)
        self.player_position = position

    def getDirection(self, way):
        direction = (0, 0)
        if way == MSTransition.Up:
            direction = (1, 0)
        elif way == MSTransition.Down:
            direction = (-1, 0)
        elif way == MSTransition.Right:
            direction = (0, 1)
        elif way == MSTransition.Left:
            direction = (0, -1)
        return direction





