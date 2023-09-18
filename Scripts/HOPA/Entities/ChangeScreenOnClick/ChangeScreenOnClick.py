from Foundation.TaskManager import TaskManager
from HOPA.ChangeScreenOnClickManager import ChangeScreenOnClickManager

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


class ChangeScreenOnClick(Enigma):

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
        self.Cur_pos = None
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
        self._Clean_Full()

    # entity setup

    def _prepare(self):
        self._load()
        self._setup()
        self.Clear_Scene()
        self.Create_Scene()
        for Movie in self.Movies_actual:
            Movie.setAlpha(1.0)

    def _load(self):
        self.param = ChangeScreenOnClickManager.getParam(self.EnigmaName)
        self.Board = self.param.Board

    def _setup(self):
        self._setup_Movies()
        self._setup_Board()

        if self.param.MapName is not None:
            self.Map = self.object.generateObject(self.param.MapName, self.param.MapName)
        if self.param.HandName is not None:
            self.Hand = self.object.generateObject(self.param.HandName, self.param.HandName)

        self._setupAllArrows()

    def _setupAllArrows(self):
        self._setup_Arrow(self.param.PrototypeArrowUp)
        self._setup_Arrow(self.param.PrototypeArrowLeft)
        self._setup_Arrow(self.param.PrototypeArrowRight)
        self._setup_Arrow(self.param.PrototypeArrowDown)

    def _setup_Movies(self):
        for name in self.param.StateNames:
            Movie = self.object.generateObject(name, name)
            Movie.setAlpha(0.0)
            self.Movies.append(Movie)

        for name in self.param.EnvironmentNames:
            Movie = self.object.generateObject(name, name)
            Movie.setAlpha(0.0)
            self.Environments_Movies.append(Movie)

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

    def _setup_Board(self):
        # init board with all None
        self.Board = [[None] * (len(self.param.Board)) for k in range(len(self.param.Board[0]))]

        total_envs = len(self.Environments_Movies)

        for i in range(len(self.param.Board)):
            for j in range(len(self.param.Board[i])):
                self.Board[i][j] = self.param.Board[i][j]

                # if passage here - set random number to set env movie here
                if self.Board[i][j] == ChangeScreenOnClickManager.BoardCell.TYPE_PASSAGE:
                    self.Board[i][j] = Mengine.rand(total_envs)

        self.Cur_pos = [[None] * 3 for i in range(3)]
        self.updateCurrentPosition()

    def _setup_Arrow(self, name):
        params = dict(Enable=False)
        Arrow = self.object.generateObject(name, name, params)
        # Arrow.setEnable(False)

        self.Arrows.append(Arrow)

    # ---- Enigma handling ---------------------------------------------------------------------------------------------

    def _playEnigma(self):
        self.tc_2 = TaskManager.createTaskChain(Repeat=True)
        with self.tc_2 as tc_1:
            tc_1.addScope(self.Speed_Changer)

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.scopeMainActivity)
            tc.addFunction(self.Started)

    def _skipEnigma(self):
        self._Clean_Full()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._Clean_Full()
        self._prepare()
        self._playEnigma()

    # utils

    def Started(self):
        self.Start = False

    def _Complete(self):
        self._Clean_Full()
        self.enigmaComplete()

    # ---- Game handling -----------------------------------------------------------------------------------------------

    def Clear_Scene(self):
        self._Destroy_Movies(self.Arrows)
        self.Arrows = []
        self.Movies_actual = []
        self.Current_Arrows = []

        self._setupAllArrows()
        for Arrow in self.Arrows:
            self.Current_Arrows.append(Arrow)

        self.return_Movies(self.Movies)
        self.return_Movies(self.Environments_Movies)

    def Create_Scene(self):
        """ update scene each frame """
        Block = ChangeScreenOnClickManager.BoardCell.TYPE_WALL

        self.Movies_actual.append(self.Movies[0])  # main
        self.Movies_actual.append(self.Movies[2])  # right door
        self.Movies_actual.append(self.Movies[3])  # left door

        if self.Cur_pos[0][1] == Block:     # top
            self.Movies_actual.append(self.Movies[1])
            self.Current_Arrows.remove(self.Arrows[0])
        if self.Cur_pos[1][2] == Block:     # right
            self.Movies_actual.remove(self.Movies[2])
            self.Current_Arrows.remove(self.Arrows[2])
        if self.Cur_pos[1][0] == Block:     # left
            self.Movies_actual.remove(self.Movies[3])
            self.Current_Arrows.remove(self.Arrows[1])
        if self.Cur_pos[2][1] == Block:     # bottom
            self.Current_Arrows.remove(self.Arrows[3])

        if len(self.Current_Arrows) == 1 and self.Cur_pos[0][1] == Block:
            self.Movies_actual.append(self.Movies[4])   # deadlock

        if self.Cur_pos[2][1] != Block:     # bottom
            for movie in self.Environments_Composition[self.Cur_pos[2][1]]:
                self.Movies_actual.append(movie)

    def scopeMainActivity(self, source):
        click_holder = Holder()

        if self.Start is False:
            self.Clear_Scene()

        if self.End:
            self.Movies[-1].setAlpha(1.0)
            source.addTask("TaskMovie2Play", Movie2=self.Movies[-1])
            source.addFunction(self._Complete)
            return

        if self.Start is False:     # do not create scene twice at start
            self.Create_Scene()
            source.addScope(self.Show_Movie, self.Movies_actual)

        # click on arrow to choose direction
        for Button, source_1 in source.addRaceTaskList(self.Current_Arrows):
            source_1.addTask("TaskEnable", Object=Button, Value=True)
            source_1.addTask("TaskMovie2ButtonClick", Movie2Button=Button)
            source_1.addFunction(click_holder.set, Button)

        with source.addParallelTask(3) as (Tc_Sound_1, Tc_Sound_2, Tc_Game):
            Tc_Sound_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_ButtonClick')
            Tc_Sound_2.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_Steps')

            Tc_Game.addFunction(self.Move_Player, click_holder)
            Tc_Game.addScope(self.Ilusory_Move, click_holder)

    def Show_Movie(self, source, array):
        for Movie, source_1 in source.addParallelTaskList(array):
            source_1.addTask("AliasObjectAlphaTo", Object=Movie, Time=self.Time, To=1.0)

    def Ilusory_Move(self, source, btn_holder):
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

        with source.addParallelTask(3) as (Tc_Hand, Tc_Labirint, Tc_Buttons):
            Tc_Hand.addTask("TaskMovie2Play", Movie2=self.Hand, Wait=False)
            Tc_Labirint.addScope(self.scopeHide_Movie, self.Movies_actual)
            Tc_Buttons.addScope(self.scopeHide_Arrows, self.Current_Arrows)

    def scopeHide_Movie(self, source, array):
        for Movie, source_1 in source.addParallelTaskList(array):
            with source_1.addParallelTask(3) as (parallel_1, parallel_2, parallel_3):
                parallel_1.addTask("AliasObjectAlphaTo", Object=Movie, Time=self.Time, To=0.0)
                parallel_2.addTask("TaskNodeScaleTo", Node=Movie.getEntityNode(),
                                   To=(self.SceneScale, self.SceneScale, self.SceneScale), Time=self.Time)
                parallel_3.addTask("TaskNodeMoveTo", Node=Movie.getEntityNode(), To=self.ScalePosition, Time=self.Time)

    def scopeHide_Arrows(self, source, array):
        for Movie, source_1 in source.addParallelTaskList(array):
            source_1.addTask("AliasObjectAlphaTo", Object=Movie, Time=self.Time, To=0.0)

    def Speed_Changer(self, source):
        source.addTask("TaskSubMovie2Play", Movie2=self.Hand, SubMovie2Name="Lantern_Idle")

    def return_Movies(self, array):
        for movie in array:
            movie.setAlpha(0.0)
            movie.setScale((1.0, 1.0, 1.0))
            node = movie.getEntityNode()
            node.setWorldPosition((0.0, 0.0, 0.0))

    def Move_Player(self, btn_holder):
        Button = btn_holder.get()
        index_arrow = self.Arrows.index(Button)

        direction = Direction.get(self.Player_Direction)
        self.updateCurrentPosition()
        self.Rotate_Board(direction)
        self.Move_Cur_Player(index_arrow)

        self._checkGameEnd()
        self.setCur_Pos(direction)
        self.updateCurrentPosition()
        direction = Direction.get(self.Player_Direction)
        self.Rotate_Board(direction)

    def _checkGameEnd(self):
        """ check if player is on finish cell and set End flag if true """
        if self.Cur_pos[1][1] == ChangeScreenOnClickManager.BoardCell.TYPE_FINISH:
            self.End = True

    def Bonus_Move(self):    # not used
        Block = ChangeScreenOnClickManager.BoardCell.TYPE_WALL
        if self.Cur_pos[1][0] == Block and self.Cur_pos[1][2] == Block and self.Cur_pos[0][1] != Block:
            click_hold = Holder()
            click_hold.set(self.Arrows[0])
            self.Move_Player(click_hold)

    def setCur_Pos(self, direction):
        reverted_direction = Direction.getReverted(direction)
        self.Rotate_Board(reverted_direction)
        self.updateBoardPosition()

    def Move_Cur_Player(self, index_arrow):
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

    def Rotate_Board(self, direction):
        if direction == Direction.Up:
            return

        temp_Array = [[None] * 3 for i in range(3)]
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
        Player_Pos = self._findPlayerPos()

        for i in range(Player_Pos[0] - 1, Player_Pos[0] + 2):
            for j in range(Player_Pos[1] - 1, Player_Pos[1] + 2):
                self.Cur_pos[i - Player_Pos[0] + 1][j - Player_Pos[1] + 1] = self.Board[i][j]

    def updateBoardPosition(self):
        Player_Pos = self._findPlayerPos()

        for i in range(Player_Pos[0] - 1, Player_Pos[0] + 2):
            for j in range(Player_Pos[1] - 1, Player_Pos[1] + 2):
                self.Board[i][j] = self.Cur_pos[i - Player_Pos[0] + 1][j - Player_Pos[1] + 1]

    def _findPlayerPos(self):
        position = (0, 0)

        for i in range(len(self.Board)):
            for j in range(len(self.Board[i])):
                if self.Board[i][j] == ChangeScreenOnClickManager.BoardCell.TYPE_START:
                    position = (i, j)
                    break

        return position

    # ---- Cleaning ----------------------------------------------------------------------------------------------------

    def _Clean_Full(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
        if self.tc_2 is not None:
            self.tc_2.cancel()
            self.tc_2 = None

        self.param = None

        self._Destroy_Movies(self.Arrows)
        self.Arrows = []

        self._Destroy_Movies(self.Movies)
        self.Movies = []

        self.Movies_actual = []
        self._Destroy_Movies(self.Environments_Movies)
        self.Environments_Movies = []

        self.Current_Arrows = []
        self.Board = []
        self.Environments_Composition = {}
        self.Cur_pos = None
        self.Player_Direction = Direction.Up

        if self.Map is not None:
            self.Map.onDestroy()
            self.Map = None
        if self.Hand is not None:
            self.Hand.onDestroy()
            self.Hand = None

        self.End = False
        self.Start = True

    def _Destroy_Movies(self, array):
        for movie in array:
            movie.onDestroy()
