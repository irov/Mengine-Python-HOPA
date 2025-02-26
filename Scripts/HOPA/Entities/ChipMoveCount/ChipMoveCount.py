from Foundation.TaskManager import TaskManager
from HOPA.ChipMoveCountManager import ChipMoveCountManager


Enigma = Mengine.importEntity("Enigma")


class ChipMoveCount(Enigma):
    def _setupPos(self):
        for i in range(2):
            self.Player_Number.append(self.param.chips[i].counter.max_number + 1)
            for j in range(2):
                self.Player_Pos.append(self.param.chips[i].start[j])
                self.Finish_pos.append(self.param.chips[i].finish[j])
        self.layers = ["number_{}".format(n) for n in range(self.Player_Number[1])]

    def _setup(self):
        self._setupPos()

        MovieSlots = self.object.getObject("Movie2_Slots")
        self.Player = 0
        self._Form_Array(MovieSlots)
        self._Create_Players(MovieSlots)
        self.Player = 1
        self._Create_Players(MovieSlots)
        self.Player = None

    def _Create_Players(self, MovieSlots):
        Slot_First_Player = MovieSlots.getMovieSlot(
            'slot_' + str(self.Player_Pos[self.Player * 2]) + '_' + str(self.Player_Pos[self.Player * 2 + 1]))
        if self.Player == 0:
            self.SlotNumbers.append(MovieSlots.getMovieSlot('slot_2_6'))
        elif self.Player == 1:
            self.SlotNumbers.append(MovieSlots.getMovieSlot('slot_6_7'))
        self.Node_Player[self.Player] = Mengine.createNode("Interender")
        MovieSlotsEntityNode = MovieSlots.getEntityNode()
        MovieSlotsEntityNode.addChild(self.Node_Player[self.Player])
        SlotFromPosition = Slot_First_Player.getWorldPosition()
        self.Node_Player[self.Player].setLocalPosition(SlotFromPosition)

        Movie_Arrow_Up = self.object.generateObject("Movie2_Button_Up" + str(self.Player), self.param.prototype_arrow_up)
        Movie_Arrow_Down = self.object.generateObject("Movie2_Button_Down" + str(self.Player), self.param.prototype_arrow_down)
        Movie_Arrow_Left = self.object.generateObject("Movie2_Button_Left" + str(self.Player), self.param.prototype_arrow_left)
        Movie_Arrow_Right = self.object.generateObject("Movie2_Button_Right" + str(self.Player), self.param.prototype_arrow_right)
        Movie_Chip = self.object.generateObject("Chip" + str(self.Player), self.param.chips[self.Player].prototype)
        MovieNumbers = self.object.generateObject("Numbers" + str(self.Player), self.param.chips[self.Player].counter.prototype)
        self.player_movie_pack.append(Movie_Chip)
        self.player_movie_pack.append(Movie_Arrow_Up)
        self.player_movie_pack.append(Movie_Arrow_Down)
        self.player_movie_pack.append(Movie_Arrow_Left)
        self.player_movie_pack.append(Movie_Arrow_Right)
        self.player_movie_pack.append(MovieNumbers)
        self._Number_reset()
        self._Change_Arrows()

        for i in range(self.Player * self.Movie_Count, self.Player * self.Movie_Count + self.Movie_Count):
            self._attachMovieToNode2(self.player_movie_pack[i], self.Node_Player[self.Player])

        self._attachMovieToNode2(self.player_movie_pack[self.Player * self.Movie_Count + 5], self.SlotNumbers[self.Player])

    def _Form_Array(self, MovieSlots):
        grid_size = self.param.grid_size
        grid0 = self.param.chips[0].grid[1][0]

        self.grid = [[0] * (grid_size[0] + 2) for i in range((grid_size[1] + 2))]
        self.game_state = [[0] * (grid_size[0] + 2) for i in range((grid_size[1] + 2))]

        for i in range((grid_size[1] + 2)):
            for j in range((grid_size[0] + 2)):
                self.grid[i][j] = (MovieSlots.getMovieSlot('slot_' + str(i) + '_' + str(j)))

        for i in range((grid_size[1] + 2)):
            for j in range((grid_size[0] + 2)):
                if self.grid[i][j] != None:
                    if j < grid0:
                        self.game_state[i][j] = "First"
                    else:
                        self.game_state[i][j] = "Second"
                else:
                    self.game_state[i][j] = None

    def _Next_Move(self):
        if self.Player == 0:
            border = "Second"
        elif self.Player == 1:
            border = "First"
        else:
            return

        if self.Arrow_Pressed == "Up":
            for i in range(self.Player_Pos[2 * self.Player], -1, -1):
                if self.game_state[i][self.Player_Pos[2 * self.Player + 1]] is None:
                    self.Move_To.append(i + 1)
                    self.Move_To.append(self.Player_Pos[2 * self.Player + 1])
                    return
        elif self.Arrow_Pressed == "Down":
            for i in range((self.Player_Pos[2 * self.Player]) + 1, len(self.game_state)):
                if self.game_state[i][self.Player_Pos[2 * self.Player + 1]] is None:
                    self.Move_To.append(i - 1)
                    self.Move_To.append(self.Player_Pos[2 * self.Player + 1])
                    return
        elif self.Arrow_Pressed == "Left":
            for j in range((self.Player_Pos[2 * self.Player + 1]) - 1, -1, -1):
                if self.game_state[(self.Player_Pos[2 * self.Player])][j] is None or self.game_state[(self.Player_Pos[2 * self.Player])][j] == border:
                    self.Move_To.append((self.Player_Pos[2 * self.Player]))
                    self.Move_To.append(j + 1)

                    return
        elif self.Arrow_Pressed == "Right":
            for j in range((self.Player_Pos[2 * self.Player + 1]), len(self.game_state[0])):
                if self.game_state[(self.Player_Pos[2 * self.Player])][j] is None or self.game_state[(self.Player_Pos[2 * self.Player])][j] == border:
                    self.Move_To.append((self.Player_Pos[2 * self.Player]))
                    self.Move_To.append(j - 1)

                    return
        else:
            return
        return

    def _scopeArrow_Move(self, source):
        with source.addRaceTask(5) as (tc_up, tc_down, tc_left, tc_right, tc_change):
            tc_up.addTask("TaskMovie2ButtonClick",
                          Movie2Button=self.player_movie_pack[self.Movie_Count * self.Player + 1])
            tc_up.addFunction(self._Ar_Up)

            tc_down.addTask("TaskMovie2ButtonClick",
                            Movie2Button=self.player_movie_pack[self.Movie_Count * self.Player + 2])
            tc_down.addFunction(self._Ar_Down)

            tc_left.addTask("TaskMovie2ButtonClick",
                            Movie2Button=self.player_movie_pack[self.Movie_Count * self.Player + 3])
            tc_left.addFunction(self._Ar_Left)

            tc_right.addTask("TaskMovie2ButtonClick",
                             Movie2Button=self.player_movie_pack[self.Movie_Count * self.Player + 4])
            tc_right.addFunction(self._Ar_Right)

            tc_change.addScope(self._scopeChange_Player)

        source.addFunction(self._Next_Move)
        source.addScope(self._Is_We_Stay)
        source.addDelay(100.0)
        source.addScope(self._scopeMove, self.Node_Player[self.Player], 500.0)
        source.addScope(self._scopeShowLayer, self.player_movie_pack[self.Movie_Count * self.Player + 5])

    def _Ar_Up(self, ):
        self.Arrow_Pressed = "Up"

    def _Ar_Down(self):
        self.Arrow_Pressed = "Down"

    def _Ar_Left(self):
        self.Arrow_Pressed = "Left"

    def _Ar_Right(self):
        self.Arrow_Pressed = "Right"

    def _Change_Pos(self):
        self.Player_Pos[2 * self.Player] = self.Move_To[-2]
        self.Player_Pos[2 * self.Player + 1] = self.Move_To[-1]

    def _Change_Player(self, first_time=False):
        if self.Player == 1:
            self.Arrow_Pressed = None
            if self.Finish[0]:
                return
            self.Player = 0
            return
        elif self.Player == 0:
            self.Arrow_Pressed = None
            if self.Finish[1]:
                return
            self.Player = 1
            return

        if first_time == 0:
            self.Arrow_Pressed = None
            self.Player = 0
            return
        elif first_time == 1:
            self.Arrow_Pressed = None
            self.Player = 1
            return

    def _scopeMove(self, source, node, time=None):
        if self.grid[self.Move_To[-2]][self.Move_To[-1]] is None or self.Arrow_Pressed is None:
            return

        posTo = self.grid[self.Move_To[-2]][self.Move_To[-1]].getWorldPosition()

        if time is None or time == 0.0:
            node.setLocalPosition(posTo)
            source.addFunction(self._Change_Pos)
        else:
            speed = 1000.0 * 200 / time
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipMoveCount_Move')
                parallel_2.addTask("TaskNodeMoveTo", Node=node, To=posTo, Speed=speed)
            source.addFunction(self._Change_Pos)

        pass

    def _Is_We_Stay(self, source):
        if (self.Player_Pos[2 * self.Player] == self.Move_To[-2]) and (
            self.Player_Pos[2 * self.Player + 1] == self.Move_To[-1]):
            self.Arrow_Pressed = None
            source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipMoveCount_Stay')
            return

    def _Other_Player(self):
        if self.Player == 0:
            return 1
        elif self.Player == 1:
            return 0

    def _scopeChange_Player(self, source):
        if self.Stop_Changing:
            source.addDelay(3000000.0)
        if self.Finish[0] or self.Finish[1]:
            self.Stop_Changing = True
        source.addTask("TaskMovie2SocketEnter", Movie2=self.player_movie_pack[self.Movie_Count * self._Other_Player()],
                       SocketName="socket")
        source.addFunction(self._Change_Arrows, False)
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipMoveCount_Change_Player')
        source.addFunction(self._Change_Player)
        source.addFunction(self._Change_Arrows, True)

        pass

    def _Change_Arrows(self, tf=False):
        for i in range(1, self.Movie_Count - 1):
            self.player_movie_pack[self.Movie_Count * self.Player + i].setEnable(tf)

    def _scopeShowLayer(self, source, movie):
        if self.Arrow_Pressed is None:
            return
        layerName = self.layers[self.Player_Number[self.Player]]
        movie.appendParam("DisableLayers", layerName)
        self._Number_decrease()
        layerName = self.layers[self.Player_Number[self.Player]]
        movie.delParam("DisableLayers", layerName)
        pass

    def _scopeStart(self, source):
        if self.Player is None:
            with source.addRaceTask(2) as (tc_Player0, tc_Player1):
                tc_Player0.addTask("TaskMovie2SocketEnter", Movie2=self.player_movie_pack[0], SocketName="socket")

                tc_Player0.addFunction(self._Change_Player, 0)
                tc_Player0.addFunction(self._Change_Arrows, True)

                tc_Player1.addTask("TaskMovie2SocketEnter", Movie2=self.player_movie_pack[self.Movie_Count],
                                   SocketName="socket")

                tc_Player1.addFunction(self._Change_Player, 1)
                tc_Player1.addFunction(self._Change_Arrows, True)
        pass

    # def _Player_Finished(self):
    #     self.Finish[self.Player] = True
    def _IsGameEnd(self, source):
        finished_players = 0
        if self.Player_Number[self.Player] <= 0:
            if (self.Player_Pos[2 * self.Player] == self.Finish_pos[2 * self.Player]) and (self.Player_Pos[2 * self.Player + 1] == self.Finish_pos[2 * self.Player + 1]):
                self.Finish[self.Player] = True
                with source.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipMoveCount_Finished')
                    parallel_2.addFunction(self._Change_Arrows)
            else:
                source.addScope(self._Chip_Return)

                return
        else:
            if (self.Player_Pos[2 * self.Player] == self.Finish_pos[2 * self.Player]) and (
                self.Player_Pos[2 * self.Player + 1] == self.Finish_pos[2 * self.Player + 1]):
                source.addScope(self._Chip_Return)

        for i in range(len(self.Finish)):
            if self.Finish[i]:
                finished_players += 1
        if self.Player_Count == finished_players:
            source.addScope(self._Complete)

    def _Complete(self, source):
        self._Clean_Full()
        self.enigmaComplete()
        pass

    def _Chip_Return(self, source):
        self.Player_Number[self.Player] = self.param.chips[self.Player].counter.max_number + 1
        self.Move_To.append(self.param.chips[1 * self.Player].start[0])
        self.Move_To.append(self.param.chips[1 * self.Player].start[1])

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipMoveCount_Return')
            parallel_2.addDelay(500.0)

        source.addFunction(self._Number_reset)
        source.addTask("TaskNodeScaleTo", Node=self.Node_Player[self.Player], To=(0.0, 0.0, 1.0), Time=400.0)
        source.addScope(self._scopeMove, self.Node_Player[self.Player])
        source.addTask("TaskNodeScaleTo", Node=self.Node_Player[self.Player], To=(1.0, 1.0, 1.0), Time=400.0)

    def _Number_reset(self):
        for layerName in self.layers:
            if layerName not in self.player_movie_pack[self.Player * self.Movie_Count + 5].getParam("DisableLayers"):
                self.player_movie_pack[self.Player * self.Movie_Count + 5].appendParam("DisableLayers", layerName)
        self._Number_decrease()
        self.player_movie_pack[self.Player * self.Movie_Count + 5].delParam("DisableLayers", self.layers[self.Player_Number[self.Player]])

    def _Number_decrease(self):
        self.Player_Number[self.Player] += -1

    def _attachMovieToNode2(self, movie, node):
        entity_node = movie.getEntityNode()
        node.addChild(entity_node)

    def _onActivate(self):
        super(ChipMoveCount, self)._onActivate()
        pass

    def __init__(self):
        super(ChipMoveCount, self).__init__()
        self.param = None
        self.tc = None
        self.SlotNumbers = []
        self.Movie_Count = 6
        self.Player_Count = 2
        self.Node_Player = [None, None]
        self.player_movie_pack = []
        self.grid = None
        self.game_state = None
        self.Player = None
        self.Arrow_Pressed = None
        self.Player_Pos = []
        self.Finish_pos = []
        self.Finish = [False, False]
        self.Player_Number = []
        self.layers = []
        self.Stop_Changing = False

        self.Move_To = [0, 0]

    def _load_param(self):
        self.param = ChipMoveCountManager.getParam(self.EnigmaName)

    def _playEnigma(self):
        self._load_param()
        self._setup()

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._scopeStart)
            tc.addScope(self._scopeArrow_Move)
            tc.addScope(self._IsGameEnd)

    def _skipEnigma(self):
        self._Clean_Full()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._Clean_Full()
        self._playEnigma()

    def _Clean_Full(self):
        if self.tc is not None:
            self.tc.cancel()
        for movie in self.player_movie_pack:
            movie.onDestroy()
        self.param = None
        self.tc = None
        self.SlotNumbers = []
        self.Movie_Count = 6
        self.Player_Count = 2
        self.Node_Player = [None, None]
        self.player_movie_pack = []
        self.grid = None
        self.game_state = None
        self.Player = None
        self.Arrow_Pressed = None
        self.Player_Pos = []
        self.Finish_pos = []
        self.Finish = [False, False]
        self.Stop_Changing = False
        self.Player_Number = []
        self.layers = []

        self.Move_To = [0, 0]

    def _onDeactivate(self):
        super(ChipMoveCount, self)._onDeactivate()
        self._Clean_Full()
