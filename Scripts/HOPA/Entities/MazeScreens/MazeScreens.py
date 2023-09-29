from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSTransition
from HOPA.Entities.MazeScreens.Room import Room
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput


Enigma = Mengine.importEntity("Enigma")
FADE_TIME = 150.0


class MazeScreens(Enigma):

    def __init__(self):
        super(MazeScreens, self).__init__()
        self.params = None
        self._rooms = {}    # {room_id: Room}
        self.__current_room = None
        self.board = None
        self.player_position = None
        self.__done_groups = []

    def _onPreparation(self):
        self._prepare()

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        self._cleanFull()

    # enigma handling

    def _playEnigma(self):
        self.__current_room.onActivate()

    def _skipEnigma(self):
        self.setComplete()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        TaskManager.runAlias("AliasFadeIn", None, FadeGroupName="Fade", To=1.0, Time=FADE_TIME)
        self._cleanFull()
        self._prepare()
        TaskManager.runAlias("AliasFadeOut", None, FadeGroupName="Fade", From=0.0, Time=FADE_TIME)
        self._playEnigma()

    # enigma flow

    def _prepare(self):
        self.params = MazeScreensManager.getSettings(self.EnigmaName)

        if self.params.win_movie_name is not None:
            win_movie = self.object.getObject(self.params.win_movie_name)
            win_movie.setEnable(False)

        self._setupRooms()
        self._setupBoard()

    def _setupRooms(self):
        for room_params in self.params.rooms.values():
            room = Room()
            room.onInitialize(self, room_params)
            room.onPreparation()

            self._rooms[room_params.id] = room

            if room_params.is_start is True:
                self.__current_room = room

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
        self.__current_room = None
        self.__done_groups = []
        self.board = []

        self.params = None

    def setComplete(self):
        if self.params.win_movie_name is not None:
            self._completeWithAnimation()
            return

        self._cleanFull()
        self.enigmaComplete()

    def _completeWithAnimation(self):
        movie = self.object.getObject(self.params.win_movie_name)

        with TaskManager.createTaskChain(Name="MazeScreensWinAnimation") as tc:
            with GuardBlockInput(tc) as guard_source:
                with guard_source.addParallelTask(2) as (guard_animation, guard_cleanup):
                    guard_animation.addEnable(movie)
                    guard_animation.addPlay(movie, Wait=True)
                    guard_cleanup.addFunction(self._cleanFull)

            tc.addFunction(self.enigmaComplete)

    # public methods

    def setCurrentRoom(self, room_id):
        if room_id is None:
            return
        if room_id not in self._rooms:
            Trace.log("Enigma", 0, "MazeScreens.setCurrentRoom: not found room with id %s" % room_id)
            return

        TaskManager.runAlias("AliasFadeIn", None, FadeGroupName="Fade", To=1.0, Time=FADE_TIME)
        if self.__current_room is not None:
            self.__current_room.onDeactivate()

        room = self._rooms[room_id]
        room.onActivate()
        TaskManager.runAlias("AliasFadeOut", None, FadeGroupName="Fade", From=0.0, Time=FADE_TIME)
        self.__current_room = room

    def getCurrentRoom(self):
        return self.__current_room

    def isGroupDone(self, group_id):
        return group_id in self.DoneGroups

    def setGroupDone(self, group_id):
        if group_id in self.__done_groups:
            Trace.log("Enigma", 0, "Group with id {!r} already done".format(group_id))
            return
        self.__done_groups.append(group_id)
        Notification.notify(Notificator.onMazeScreensGroupDone, group_id)

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

        self.setCurrentRoom(room.id)

        if self.params.should_rotate_board is True:
            self.rotateBoard(way)

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

    def rotateBoard(self, direction):
        if direction == "right":
            self.board = [list(row) for row in zip(*self.board[::-1])]
        elif direction == "left":
            self.board = [list(row) for row in zip(*self.board)]





