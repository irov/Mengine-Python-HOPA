from HOPA.MazeScreensManager import MazeScreensManager
from HOPA.MazeScreensManager import MSTransition
from HOPA.Entities.MazeScreens.Room import Room
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput
from HOPA.TransitionManager import TransitionManager


Enigma = Mengine.importEntity("Enigma")
FADE_TIME = 350.0


class MazeScreens(Enigma):

    """ Doc: https://wonderland-games.atlassian.net/wiki/spaces/HOG/pages/2146369537/MazeScreens """

    def __printMap(self):
        if _DEVELOPMENT is False:
            return

        print " BOARD ".center(15, "-")
        for i in range(len(self.board)):
            line = ""
            for j in range(len(self.board[i])):
                line += str(self.board[i][j] if self.board[i][j] else MazeScreensManager.CELL_TYPE_WALL).ljust(4, " ")
            print line
        print " Player position is", self.player_position, "room", self.board[self.player_position[0]][self.player_position[1]]

    def __init__(self):
        super(MazeScreens, self).__init__()
        self.params = None
        self._rooms = {}    # {room_id: Room}
        self.__current_room = None
        self.board = None
        self.player_position = None
        self.__done_groups = []

    def _onPreparation(self):
        super(MazeScreens, self)._onPreparation()
        self._prepare()

    def _onActivate(self):
        super(MazeScreens, self)._onActivate()

    def _onDeactivate(self):
        super(MazeScreens, self)._onDeactivate()
        self._cleanFull()

        if TaskManager.existTaskChain("MazeScreensReset") is True:
            TaskManager.cancelTaskChain("MazeScreensReset")
        if TaskManager.existTaskChain("MazeScreensWinAnimation") is True:
            TaskManager.cancelTaskChain("MazeScreensWinAnimation")
        if TaskManager.existTaskChain("MazeScreensChangeRoom") is True:
            TaskManager.cancelTaskChain("MazeScreensChangeRoom")

    # enigma handling

    def _playEnigma(self):
        self.__printMap()
        self.__current_room.onActivate()

    def _skipEnigma(self):
        self.setComplete()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        def _reset():
            self._cleanFull()
            self._prepare()
            self._playEnigma()

        with TaskManager.createTaskChain(Name="MazeScreensReset") as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addTask("AliasFadeIn", FadeGroupName="Fade", To=1.0, Time=FADE_TIME)
                guard_source.addFunction(_reset)
                guard_source.addTask("AliasFadeOut", FadeGroupName="Fade", From=1.0, Time=FADE_TIME)

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
        self.toggleNavBackButton(True)

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
                    guard_animation.addDelay(1000)
                    guard_cleanup.addFunction(self._cleanFull)

            tc.addFunction(self.enigmaComplete)

    # public methods

    def setCurrentRoom(self, room_id):
        if room_id is None:
            return
        if room_id not in self._rooms:
            Trace.log("Entity", 0, "MazeScreens.setCurrentRoom: not found room with id %s" % room_id)
            return

        def _update():
            if self.__current_room is not None:
                self.__current_room.onDeactivate()

            room = self._rooms[room_id]
            room.onActivate()

            self.__current_room = room

        with TaskManager.createTaskChain(Name="MazeScreensChangeRoom") as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addTask("AliasFadeIn", FadeGroupName="Fade", To=1.0, Time=FADE_TIME)
                guard_source.addFunction(_update)
                guard_source.addTask("AliasFadeOut", FadeGroupName="Fade", From=1.0, Time=FADE_TIME)

    def getCurrentRoom(self):
        return self.__current_room

    def isGroupDone(self, group_id):
        return group_id in self.__done_groups

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

        direction = self.getDirectionVector(way)
        position = (
            self.player_position[0] + direction[0],
            self.player_position[1] + direction[1],
        )
        room = self.board[position[0]][position[1]]

        if room is None:
            Trace.log("Entity", 0, "MazeScreens impossible to move player {!r} - None on this position {}".format(way, position))
            return

        self.setCurrentRoom(room.id)

        self.player_position = position
        self.__printMap()

    def getDirectionVector(self, way):
        vector = (0, 0)
        if way == MSTransition.Up:
            vector = (-1, 0)
        elif way == MSTransition.Down:
            vector = (1, 0)
        elif way == MSTransition.Right:
            vector = (0, 1)
        elif way == MSTransition.Left:
            vector = (0, -1)
        return vector

    def getCurrentRoomPosition(self):
        position = (0, 0)
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == self.__current_room:
                    position = (i, j)
                    break
        return position

    def toggleNavBackButton(self, state):
        """ toggle transition back button interactive """
        TransitionManager.s_transitionBackObject.setInteractive(state)







