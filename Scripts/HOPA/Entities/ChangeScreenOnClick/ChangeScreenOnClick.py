from Foundation.TaskManager import TaskManager
from HOPA.ChangeScreenOnClickManager import ChangeScreenOnClickManager


Enigma = Mengine.importEntity("Enigma")


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
        self.Player_Diraction = 0
        self.Map = None
        self.Hand = None
        self.Time = 250.0
        self.Back_Track_Diraction = []
        self.End = False
        self.Start = True
        self.SceneScale = 1.0
        self.ScalePosition = None
        pass

    def _prepare(self):
        self._load_param()
        self._setup()
        self.Clear_Scene()
        self.Create_Scene()
        for Movie in self.Movies_actual:
            Movie.setAlpha(1.0)

    def _onPreparation(self):
        super(ChangeScreenOnClick, self)._onPreparation()

        self._prepare()

    def _onActivate(self):
        super(ChangeScreenOnClick, self)._onActivate()
        pass

    def _playEnigma(self):
        self.tc_2 = TaskManager.createTaskChain(Repeat=True)
        with self.tc_2 as tc_1:
            tc_1.addScope(self.Speed_Changer)

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.All_work)
            tc.addFunction(self.Started)

    def Started(self):
        self.Start = False

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
        Block = "X"

        self.Movies_actual.append(self.Movies[0])
        self.Movies_actual.append(self.Movies[2])
        self.Movies_actual.append(self.Movies[3])

        if self.Cur_pos[0][1] == Block:
            self.Movies_actual.append(self.Movies[1])
            self.Current_Arrows.remove(self.Arrows[0])
        if self.Cur_pos[1][2] == Block:
            self.Movies_actual.remove(self.Movies[2])
            self.Current_Arrows.remove(self.Arrows[2])
        if self.Cur_pos[1][0] == Block:
            self.Movies_actual.remove(self.Movies[3])
            self.Current_Arrows.remove(self.Arrows[1])
        if self.Cur_pos[2][1] == Block:
            self.Current_Arrows.remove(self.Arrows[3])

        if len(self.Current_Arrows) == 1 and self.Cur_pos[0][1] == Block:
            self.Movies_actual.append(self.Movies[4])
        if self.Cur_pos[2][1] != Block:
            for movie in self.Environments_Composition[self.Cur_pos[2][1]]:
                self.Movies_actual.append(movie)

    def All_work(self, source):
        click_holder = Holder()
        if self.Start is False:
            self.Clear_Scene()

        if self.End:
            self.Movies[-1].setAlpha(1.0)
            source.addTask("TaskMovie2Play", Movie2=self.Movies[-1])
            source.addFunction(self._Complete)

        else:
            if self.Start is False:
                self.Create_Scene()
                source.addScope(self.Show_Movie, self.Movies_actual)

            for Button, source_1 in source.addRaceTaskList(self.Current_Arrows):
                source_1.addTask("TaskEnable", Object=Button, Value=True)
                source_1.addTask("TaskMovie2ButtonClick", Movie2Button=Button)
                source_1.addFunction(click_holder.set, Button)
            with source.addParallelTask(3) as (Tc_Sound_1, Tc_Sound_2, Tc_Game):
                Tc_Sound_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_ButtonClick')
                Tc_Game.addFunction(self.Move_Player, click_holder)
                Tc_Sound_2.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChangeScreenOnClick_Steps')
                Tc_Game.addScope(self.Ilusory_Move, click_holder)

    def Show_Movie(self, source, array):
        for Movie, source_1 in source.addParallelTaskList(array):
            source_1.addTask("AliasObjectAlphaTo", Object=Movie, Time=self.Time, To=1.0)

    def Ilusory_Move(self, source, btn_holder):
        Button = btn_holder.get()
        index_arrow = self.Arrows.index(Button)
        self.ScalePosition = (-300.0, -200.0, 0.0)
        self.SceneScale = 1.4
        if index_arrow == 1:
            self.ScalePosition = (0.0, -200.0, 0.0)
        elif index_arrow == 2:
            self.ScalePosition = (-500.0, -200.0, 0.0)
        elif index_arrow == 3:
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

        Diraction = abs(self.Player_Diraction % 4)
        self.getCur_Pos()
        self.Rotate_Board(Diraction)
        self.Move_Cur_Player(index_arrow)

        self._IsGameEnd()
        self.setCur_Pos(Diraction)
        self.getCur_Pos()
        Diraction = abs(self.Player_Diraction % 4)
        self.Rotate_Board(Diraction)

    def Bonus_Move(self):
        Block = "X"
        if self.Cur_pos[1][0] == Block and self.Cur_pos[1][2] == Block and self.Cur_pos[0][1] != Block:
            click_hold = Holder()
            click_hold.set(self.Arrows[0])
            self.Move_Player(click_hold)

    def setCur_Pos(self, Diraction):
        revert_Diraction = (4 - Diraction) % 4
        self.Rotate_Board(revert_Diraction)
        self.getCur_Pos(False)

    def Move_Cur_Player(self, index_arrow):
        if index_arrow == 0:
            self.Player_Diraction += 0
            self.Back_Track_Diraction.append(0)

            self.Cur_pos[1][1], self.Cur_pos[0][1] = self.Cur_pos[0][1], self.Cur_pos[1][1]

        elif index_arrow == 3:
            self.Player_Diraction += self.Back_Track_Diraction.pop(-1)
            self.Cur_pos[1][1], self.Cur_pos[2][1] = self.Cur_pos[2][1], self.Cur_pos[1][1]


        elif index_arrow == 1:
            self.Player_Diraction += 1
            self.Back_Track_Diraction.append(-1)

            self.Cur_pos[1][1], self.Cur_pos[1][0] = self.Cur_pos[1][0], self.Cur_pos[1][1]

        elif index_arrow == 2:
            self.Player_Diraction += -1
            self.Back_Track_Diraction.append(1)

            self.Cur_pos[1][1], self.Cur_pos[1][2] = self.Cur_pos[1][2], self.Cur_pos[1][1]

    def Rotate_Board(self, Diraction):
        temp_Array = [[None] * (3) for i in range(3)]
        if Diraction == 0:
            return

        for i in range(3):
            for j in range(3):
                temp_Array[i][j] = self.Cur_pos[i][j]

        if Diraction == 2:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[2 - i][2 - j]

        elif Diraction == 1:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[2 - j][i]
        elif Diraction == 3:
            for i in range(3):
                for j in range(3):
                    self.Cur_pos[i][j] = temp_Array[j][2 - i]

    def getCur_Pos(self, Gett=True):
        for i in range(len(self.Board)):
            for j in range(len(self.Board[i])):
                if self.Board[i][j] == 'S':
                    Player_Pos = (i, j)
                    break
        if Gett:
            for i in range(Player_Pos[0] - 1, Player_Pos[0] + 2):
                for j in range(Player_Pos[1] - 1, Player_Pos[1] + 2):
                    self.Cur_pos[i - Player_Pos[0] + 1][j - Player_Pos[1] + 1] = self.Board[i][j]

        else:
            for i in range(Player_Pos[0] - 1, Player_Pos[0] + 2):
                for j in range(Player_Pos[1] - 1, Player_Pos[1] + 2):
                    self.Board[i][j] = self.Cur_pos[i - Player_Pos[0] + 1][j - Player_Pos[1] + 1]

    def _load_param(self):
        self.param = ChangeScreenOnClickManager.getParam(self.EnigmaName)
        self.Board = self.param.Board
        pass

    def _setup(self):
        self._setup_Movies()
        self._setup_Board()

        self.Map = self.object.generateObject(self.param.MapName, self.param.MapName)
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

        for j in range(len(self.Environments_Movies)):
            ii = Mengine.rand(10000)
            count = Mengine.rand(len(self.Environments_Movies) - 4) + 2

            for i in range(count):
                temp_Env = []
                temp_Env.append(self.Environments_Movies[ii % len(self.Environments_Movies)])
            self.Environments_Composition[j] = temp_Env

    def _setup_Board(self):
        Passage = '.'
        self.Board = [[None] * (len(self.param.Board)) for k in range(len(self.param.Board[0]))]
        for i in range(len(self.param.Board)):
            for j in range(len(self.param.Board[i])):
                self.Board[i][j] = self.param.Board[i][j]
                if self.Board[i][j] == Passage:
                    self.Board[i][j] = Mengine.rand(9)

        self.Cur_pos = [[None] * (3) for i in range(3)]
        self.getCur_Pos()

    def _setup_Arrow(self, name):
        params = dict(Enable=False)
        Arrow = self.object.generateObject(name, name, params)
        # Arrow.setEnable(False)

        self.Arrows.append(Arrow)

    def _IsGameEnd(self):
        if self.Cur_pos[1][1] == "F":
            self.End = True
        pass

    def _Complete(self):
        self._Clean_Full()
        self.enigmaComplete()
        pass

    def _skipEnigma(self):
        self._Clean_Full()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._Clean_Full()
        self._prepare()
        self._playEnigma()

    def _Clean_Full(self):
        if self.tc is not None:
            self.tc.cancel()
        if self.tc_2 is not None:
            self.tc_2.cancel()

        self.tc = None
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
        self.Player_Diraction = 0
        if self.Map != None:
            self.Map.onDestroy()
        self.Map = None
        if self.Hand != None:
            self.Hand.onDestroy()
        self.Hand = None
        self.speed = 600.0
        self.Last_Move = 0
        self.End = False

    def _Destroy_Movies(self, array):
        for movie in array:
            movie.onDestroy()

    def _onDeactivate(self):
        super(ChangeScreenOnClick, self)._onDeactivate()
        self._Clean_Full()
