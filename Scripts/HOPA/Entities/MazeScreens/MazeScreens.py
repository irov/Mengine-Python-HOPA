from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSTransition
from HOPA.Entities.MazeScreens.Room import Room
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput


Enigma = Mengine.importEntity("Enigma")
FADE_TIME = 150.0


class MazeScreens(Enigma):

    def __printMap(self):
        if _DEVELOPMENT is False:
            return

        print " BOARD ".center(15, "-")
        for i in range(len(self.board)):
            line = ""
            for j in range(len(self.board[i])):
                line += str(self.board[i][j] if self.board[i][j] else "X").ljust(4, " ")
            print line
        print " Player position ", self.player_position, self.player_direction, self.board[self.player_position[0]][self.player_position[1]]

    def __init__(self):
        super(MazeScreens, self).__init__()
        self.params = None
        self._rooms = {}    # {room_id: Room}
        self.__current_room = None
        self.board = None
        self.player_position = None
        self.player_direction = None
        self.__done_groups = []

    def _onPreparation(self):
        self._prepare()

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        self._cleanFull()

    # enigma handling

    def _playEnigma(self):
        self.__printMap()
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

        for i in range(graph.height):
            self.board.append([])
            for j in range(graph.width):

                cell = graph.data[i][j]
                if cell == MazeScreensManager.CELL_TYPE_WALL:
                    self.board[i].append(None)
                    continue

                room = self._rooms[cell]
                self.board[i].append(room)

                if room == self.__current_room:
                    self.player_position = (i, j)
                    print "Initial player position: {} ({})".format(self.player_position, room.id)

        self.player_direction = MSTransition.Up

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
            Trace.log("Entity", 0, "MazeScreens.setCurrentRoom: not found room with id %s" % room_id)
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
            Trace.log("Entity", 0, "Group with id {!r} already done".format(group_id))
            return
        self.__done_groups.append(group_id)
        Notification.notify(Notificator.onMazeScreensGroupDone, group_id)

    def movePlayer(self, way):
        if way == MSTransition.Win:
            self.setComplete()
            return 

        if way == MSTransition.Down:
            move_direction = self.getRevertedDirection(self.player_direction)
        else:
            move_direction = (way + self.player_direction) % 4
            self.rotatePlayer(way)

        direction = self.getDirectionVector(move_direction)
        position = (
            self.player_position[0] + direction[0],
            self.player_position[1] + direction[1],
        )
        room = self.board[position[0]][position[1]]

        if room is None:
            Trace.log("Entity", 0, "MazeScreens impossible to move player {!r} - None on this position {}".format(way, position))
            return

        self.setCurrentRoom(room.id)

        self.player_position = self.getCurrentRoomPosition()
        self.__printMap()

    def getDirectionVector(self, direction):
        vector = (0, 0)
        if direction == MSTransition.Up:
            vector = (-1, 0)
        elif direction == MSTransition.Down:
            vector = (1, 0)
        elif direction == MSTransition.Right:
            vector = (0, 1)
        elif direction == MSTransition.Left:
            vector = (0, -1)
        return vector

    def getDirection(self, way):
        return abs(way % 4)

    def getRevertedDirection(self, way):
        return abs((4 - way) % 4)

    def rotatePlayer(self, way):
        self.player_direction = self.getDirection(self.player_direction + MSTransition.convert(way))

    def getCurrentRoomPosition(self):
        position = (0, 0)
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == self.__current_room:
                    position = (i, j)
                    break
        return position







