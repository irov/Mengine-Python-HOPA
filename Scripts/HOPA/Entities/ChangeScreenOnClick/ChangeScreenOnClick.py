from Foundation.TaskManager import TaskManager
from HOPA.ChangeScreenOnClickManager import ChangeScreenOnClickManager
from HOPA.ChangeScreenOnClickManager import BoardCell

Enigma = Mengine.importEntity("Enigma")


class Direction(object):
    Up = 0
    Left = 1
    Right = 2
    Down = 3

    @staticmethod
    def get(number):
        return abs(number % 4)

    @staticmethod
    def getReverted(number):
        return abs((4 - number) % 4)


class Cell(object):
    def __init__(self):
        self.type = None
        self.params = None
        self.env = None

    def setup(self, value):
        simple_types = [BoardCell.Passage, BoardCell.Wall, BoardCell.Start, BoardCell.Finish]

        for simple_type in simple_types:
            if value == simple_type:
                self.type = simple_type
                self.params = None
                return True

        for gate_type in [BoardCell.Gate, BoardCell.Lever]:
            if value[0] == gate_type:
                self.type = gate_type
                target_number = value[1:]
                self.params = {"target": int(target_number)}
                return True

        Trace.log("Entity", 0, "ChangeScreenOnClick unknown cell type {!r}".format(value))

        self.type = BoardCell.Wall
        self.params = None
        return False

    def equalTo(self, board_type):
        return self.type == board_type

    def isEmpty(self):
        return self.type is None

    def __repr__(self):
        return str(self.type)


class ChangeScreenOnClick(Enigma):

    def __printMap(self):   # todo: delete after gates integration
        if _DEVELOPMENT is False:
            return

        print " BOARD ".center(15, "-")
        for i in range(len(self.Board)):
            line = ""
            for j in range(len(self.Board[i])):
                line += str(self.Board[i][j]).ljust(3, " ")
            print line
        print " Cur_Pos ".center(15, "-")
        for i in range(len(self.Cur_pos)):
            line = ""
            for j in range(len(self.Cur_pos[i])):
                line += str(self.Cur_pos[i][j]).ljust(3, " ")
            print line
        print " ".center(15, "-")

    def __init__(self):
        super(ChangeScreenOnClick, self).__init__()
        self.tc = None
        self.tc_2 = None
        self.param = None
        self.Arrows = []
        self.Current_Arrows = []
        self.Board = []
        self.Movies = []
        self.Movies_actual = []
        self.Environments_Movies = []
        self.Environments_Composition = {}
        self.Cur_pos = []
        self.Player_Direction = Direction.Up
        self.Map = None
        self.Hand = None
        self.Time = 250.0
        self.Back_Track_Direction = []
        self.End = False
        self.Start = True
        self.SceneScale = 1.0
        self.ScalePosition = None

    def _onPreparation(self):
        self._prepare()

    def _onDeactivate(self):
        self._cleanFull()

    # entity setup

    def _prepare(self):
        self._load()
        self._setup()
        self.clearScene()
        self.createScene()
        for movie in self.Movies_actual:
            movie.setAlpha(1.0)

    def _load(self):
        self.param = ChangeScreenOnClickManager.getParam(self.EnigmaName)

    def _setup(self):
        self._setupMovies()
        self._setupBoard()

        if self.param.MapName is not None:
            self.Map = self.object.generateObject(self.param.MapName, self.param.MapName)
        if self.param.HandName is not None:
            self.Hand = self.object.generateObject(self.param.HandName, self.param.HandName)

        self._setupAllArrows()

    def _setupAllArrows(self):
        self._setupArrow(self.param.PrototypeArrowUp)
        self._setupArrow(self.param.PrototypeArrowLeft)
        self._setupArrow(self.param.PrototypeArrowRight)
        self._setupArrow(self.param.PrototypeArrowDown)

    def _setupMovies(self):
        for name in self.param.StateNames:
            movie = self.object.generateObject(name, name)
            movie.setAlpha(0.0)
            self.Movies.append(movie)

        for name in self.param.EnvironmentNames:
            movie = self.object.generateObject(name, name)
            movie.setAlpha(0.0)
            self.Environments_Movies.append(movie)

        total_envs = len(self.Environments_Movies)

        for j in range(total_envs):
            ii = Mengine.rand(10000)
            # count = Mengine.rand(total_envs - 4) + 2
            #
            # for i in range(count):   # fixme
            #     temp_Env = []
            #     temp_Env.append(self.Environments_Movies[ii % total_envs])

            temp_Env = [self.Environments_Movies[ii % total_envs]]

            self.Environments_Composition[j] = temp_Env

    def _setupBoard(self):
        # self.Board = [[None] * (len(self.param.Board)) for _ in range(len(self.param.Board[0]))]
        self.Board = []

        total_envs = len(self.Environments_Movies)

        for i in range(len(self.param.Board)):
            self.Board.append([])
            for j in range(len(self.param.Board[i])):
                cell = Cell()
                cell.setup(self.param.Board[i][j])

                if cell.equalTo(BoardCell.Wall) is False:
                    cell.env = Mengine.rand(total_envs)
                # cell.env = Mengine.rand(total_envs)

                self.Board[i].append(cell)

        self.Cur_pos = [[None] * 3 for _ in range(3)]
        self.updateCurrentPosition()

    def _setupArrow(self, name):
        params = dict(Enable=False)
        arrow = self.object.generateObject(name, name, params)
        # arrow.setEnable(False)

        self.Arrows.append(arrow)

    # ---- Enigma handling ---------------------------------------------------------------------------------------------

    def _playEnigma(self):
        self.tc_2 = TaskManager.createTaskChain(Repeat=True)
        with self.tc_2 as tc:
            tc.addScope(self.scopeSpeedChanger)

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.scopeMainActivity)
            tc.addFunction(self.setStarted)

    def _skipEnigma(self):
        self._cleanFull()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._cleanFull()
        self._prepare()
        self._playEnigma()

    # utils

    def setStarted(self):
        self.Start = False

    def setComplete(self):
        self._cleanFull()
        self.enigmaComplete()

    # ---- Game handling -----------------------------------------------------------------------------------------------

    def clearScene(self):
        self._destroyMovies(self.Arrows)
        self.Arrows = []
        self.Movies_actual = []
        self.Current_Arrows = []

        self._setupAllArrows()
        for arrow in self.Arrows:
            self.Current_Arrows.append(arrow)

        self.returnMovies(self.Movies)
        self.returnMovies(self.Environments_Movies)

    def createScene(self):
        """ update scene each frame """
        block = BoardCell.Wall

        self.Movies_actual.append(self.Movies[0])  # main
        self.Movies_actual.append(self.Movies[2])  # right door
        self.Movies_actual.append(self.Movies[3])  # left door

        if self.Cur_pos[0][1].equalTo(block):     # top
            self.Movies_actual.append(self.Movies[1])
            self.Current_Arrows.remove(self.Arrows[0])
        if self.Cur_pos[1][2].equalTo(block):     # right
            self.Movies_actual.remove(self.Movies[2])
            self.Current_Arrows.remove(self.Arrows[2])
        if self.Cur_pos[1][0].equalTo(block):     # left
            self.Movies_actual.remove(self.Movies[3])
            self.Current_Arrows.remove(self.Arrows[1])
        if self.Cur_pos[2][1].equalTo(block):     # bottom
            self.Current_Arrows.remove(self.Arrows[3])

        if len(self.Current_Arrows) == 1 and self.Cur_pos[0][1].equalTo(block):
            self.Movies_actual.append(self.Movies[4])   # deadlock

        if self.Cur_pos[2][1].equalTo(block) is False:     # bottom
            for movie in self.Environments_Composition[self.Cur_pos[2][1].env]:
                self.Movies_actual.append(movie)

    def scopeMainActivity(self, source):
        self.__printMap()
        click_holder = Holder()

        if self.Start is False:
            self.clearScene()

        if self.End:
            self.Movies[-1].setAlpha(1.0)
            source.addTask("TaskMovie2Play", Movie2=self.Movies[-1])
            source.addFunction(self.setComplete)
            return

        if self.Start is False:     # do not create scene twice at start
            self.createScene()
            source.addScope(self.scopeShowMovie, self.Movies_actual)

        # click on arrow to choose direction
        for arrow_button, tc_arrow in source.addRaceTaskList(self.Current_Arrows):
            tc_arrow.addTask("TaskEnable", Object=arrow_button, Value=True)
            tc_arrow.addTask("TaskMovie2ButtonClick", Movie2Button=arrow_button)
            tc_arrow.addFunction(click_holder.set, arrow_button)

        with source.addParallelTask(3) as (tc_sound_1, tc_sound_2, tc_game):
            tc_sound_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_ButtonClick')
            tc_sound_2.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_Steps')

            tc_game.addFunction(self.movePlayer, click_holder)
            tc_game.addScope(self.scopeIllusoryMove, click_holder)

    def scopeShowMovie(self, source, array):
        for movie, source_1 in source.addParallelTaskList(array):
            source_1.addTask("AliasObjectAlphaTo", Object=movie, Time=self.Time, To=1.0)

    def scopeIllusoryMove(self, source, btn_holder):
        Button = btn_holder.get()
        index_arrow = self.Arrows.index(Button)

        self.ScalePosition = (-300.0, -200.0, 0.0)
        self.SceneScale = 1.4
        if index_arrow == Direction.Left:
            self.ScalePosition = (0.0, -200.0, 0.0)
        elif index_arrow == Direction.Right:
            self.ScalePosition = (-500.0, -200.0, 0.0)
        elif index_arrow == Direction.Down:
            self.ScalePosition = (0.0, 0.0, 0.0)
            self.SceneScale = 1

        with source.addParallelTask(3) as (tc_hand, tc_labyrinth, tc_buttons):
            tc_hand.addTask("TaskMovie2Play", Movie2=self.Hand, Wait=False)
            tc_labyrinth.addScope(self.scopeHideMovie, self.Movies_actual)
            tc_buttons.addScope(self.scopeHideArrows, self.Current_Arrows)

    def scopeHideMovie(self, source, array):
        for movie, source_1 in source.addParallelTaskList(array):
            with source_1.addParallelTask(3) as (parallel_1, parallel_2, parallel_3):
                parallel_1.addTask("AliasObjectAlphaTo", Object=movie, Time=self.Time, To=0.0)
                parallel_2.addTask("TaskNodeScaleTo", Node=movie.getEntityNode(),
                                   To=(self.SceneScale, self.SceneScale, self.SceneScale), Time=self.Time)
                parallel_3.addTask("TaskNodeMoveTo", Node=movie.getEntityNode(), To=self.ScalePosition, Time=self.Time)

    def scopeHideArrows(self, source, array):
        for movie, source_1 in source.addParallelTaskList(array):
            source_1.addTask("AliasObjectAlphaTo", Object=movie, Time=self.Time, To=0.0)

    def scopeSpeedChanger(self, source):
        source.addTask("TaskSubMovie2Play", Movie2=self.Hand, SubMovie2Name="Lantern_Idle")

    def returnMovies(self, array):
        for movie in array:
            movie.setAlpha(0.0)
            movie.setScale((1.0, 1.0, 1.0))
            node = movie.getEntityNode()
            node.setWorldPosition((0.0, 0.0, 0.0))

    def movePlayer(self, btn_holder):
        button = btn_holder.get()
        index_arrow = self.Arrows.index(button)

        direction = Direction.get(self.Player_Direction)
        self.updateCurrentPosition()
        self.rotateBoard(direction)
        self.moveCurrentPlayer(index_arrow)

        self._checkGameEnd()
        self.setCur_Pos(direction)
        self.updateCurrentPosition()
        direction = Direction.get(self.Player_Direction)
        self.rotateBoard(direction)

    def _checkGameEnd(self):
        """ check if player is on finish cell and set End flag if true """
        if self.Cur_pos[1][1].equalTo(BoardCell.Finish):
            self.End = True

    def moveBonus(self):    # not used
        block = BoardCell.Wall

        if all([self.Cur_pos[1][0].equalTo(block) is True,
                self.Cur_pos[1][2].equalTo(block) is True,
                self.Cur_pos[0][1].equalTo(block) is False]):
            click_hold = Holder()
            click_hold.set(self.Arrows[0])
            self.movePlayer(click_hold)

    def setCur_Pos(self, direction):
        reverted_direction = Direction.getReverted(direction)
        self.rotateBoard(reverted_direction)
        self.updateBoardPosition()

    def moveCurrentPlayer(self, index_arrow):
        if index_arrow == Direction.Up:
            self.Player_Direction += 0
            self.Back_Track_Direction.append(0)

            self.Cur_pos[1][1], self.Cur_pos[0][1] = self.Cur_pos[0][1], self.Cur_pos[1][1]

        elif index_arrow == Direction.Down:
            self.Player_Direction += self.Back_Track_Direction.pop(-1)

            self.Cur_pos[1][1], self.Cur_pos[2][1] = self.Cur_pos[2][1], self.Cur_pos[1][1]

        elif index_arrow == Direction.Left:
            self.Player_Direction += 1
            self.Back_Track_Direction.append(-1)

            self.Cur_pos[1][1], self.Cur_pos[1][0] = self.Cur_pos[1][0], self.Cur_pos[1][1]

        elif index_arrow == Direction.Right:
            self.Player_Direction += -1
            self.Back_Track_Direction.append(1)

            self.Cur_pos[1][1], self.Cur_pos[1][2] = self.Cur_pos[1][2], self.Cur_pos[1][1]

    def rotateBoard(self, direction):
        if direction == Direction.Up:
            return

        temp_Array = [[None] * 3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                temp_Array[i][j] = self.Cur_pos[i][j]

        if direction == Direction.Right:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[2 - i][2 - j]

        elif direction == Direction.Left:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[2 - j][i]

        elif direction == Direction.Down:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[j][2 - i]

    def updateCurrentPosition(self):
        player_pos = self._findPlayerPos()

        for i in range(player_pos[0] - 1, player_pos[0] + 2):
            for j in range(player_pos[1] - 1, player_pos[1] + 2):
                self.Cur_pos[i - player_pos[0] + 1][j - player_pos[1] + 1] = self.Board[i][j]

    def updateBoardPosition(self):
        player_pos = self._findPlayerPos()

        for i in range(player_pos[0] - 1, player_pos[0] + 2):
            for j in range(player_pos[1] - 1, player_pos[1] + 2):
                self.Board[i][j] = self.Cur_pos[i - player_pos[0] + 1][j - player_pos[1] + 1]

    def _findPlayerPos(self):
        position = (0, 0)

        for i in range(len(self.Board)):
            for j in range(len(self.Board[i])):
                if self.Board[i][j].equalTo(BoardCell.Start):
                    position = (i, j)
                    break

        return position

    # ---- Cleaning ----------------------------------------------------------------------------------------------------

    def _cleanFull(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
        if self.tc_2 is not None:
            self.tc_2.cancel()
            self.tc_2 = None

        self.param = None

        self._destroyMovies(self.Arrows)
        self.Arrows = []

        self._destroyMovies(self.Movies)
        self.Movies = []

        self.Movies_actual = []
        self._destroyMovies(self.Environments_Movies)
        self.Environments_Movies = []

        self.Current_Arrows = []
        self.Board = []
        self.Environments_Composition = {}
        self.Cur_pos = []
        self.Player_Direction = Direction.Up

        if self.Map is not None:
            self.Map.onDestroy()
            self.Map = None
        if self.Hand is not None:
            self.Hand.onDestroy()
            self.Hand = None

        self.End = False
        self.Start = True

    def _destroyMovies(self, array):
        for movie in array:
            movie.onDestroy()
