from Foundation.TaskManager import TaskManager
from HOPA.ChipGravitySliderManager import ChipGravitySliderManager


Enigma = Mengine.importEntity("Enigma")


class ChipGravitySlider(Enigma):
    def _onActivate(self):
        super(ChipGravitySlider, self)._onActivate()
        pass

    def __init__(self):
        super(ChipGravitySlider, self).__init__()
        self.tc = None
        self.param = None
        self.Movie_Slots_Grid = None
        self.Movie_Slots_Start = None
        self.ChipNumber = None
        self.Chips = []
        self.Blocks = []
        self.Arrows = []
        self.Finish = []
        self.First_Block = []
        self.One_Block_Hight = 0
        self.One_Block_Width = 0
        self.Board_State = []
        self.Chip_State = []
        self.speed = 600.0
        pass

    def _playEnigma(self):
        self._load_param()
        self._setup()

        click_holder = Holder()
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            for Button, source_1 in tc.addRaceTaskList(self.Arrows):
                source_1.addTask("TaskMovie2ButtonClick", Movie2Button=Button)
                source_1.addFunction(click_holder.set, Button)
            with tc.addParallelTask(2) as (Tc_Sound_1, Tc_Game):
                Tc_Sound_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipGravitySlider_ButtonClick')
                Tc_Game.addScope(self._scopeMove_Blocks, click_holder)
            for k, source1 in tc.addParallelTaskList(range(self.ChipNumber)):
                source1.addScope(self._scopeMove_Chips, k)
            tc.addFunction(self._IsGameEnd)

    def _load_param(self):
        self.param = ChipGravitySliderManager.getParam(self.EnigmaName)
        self.Movie_Slots_Grid = self.object.getObject(self.param.movie_slots)
        self.Movie_Slots_Start = self.object.getObject(self.param.MovieSlotsStart)
        self.ChipNumber = self.param.ChipNumber

    def _setup(self):
        self._setup_Chips()
        self._setup_Arrows()
        self._setup_Board()

        pass

    def _setup_Arrows(self):
        MovieSlotsEntityNode = self.Movie_Slots_Grid.getEntityNode()
        if self.param.prototype_arrow_left != None or self.param.prototype_arrow_right != None:
            for i in range(1, self.param.grid_size[0] + 1):
                Movie_Arrow_Left = self.object.generateObject("Movie2_Button_Left_" + str(i), self.param.prototype_arrow_left)
                Movie_Arrow_Right = self.object.generateObject("Movie2_Button_Right_" + str(i), self.param.prototype_arrow_right)
                Movie_Slot_Left = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(i) + '_' + str(1))
                Movie_Slot_right = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(i) + '_' + str(6))

                node_left = Movie_Arrow_Left.getEntityNode()
                node_right = Movie_Arrow_Right.getEntityNode()

                Movie_Slot_Left.addChild(node_left)
                Movie_Slot_right.addChild(node_right)

                self.Arrows.append(Movie_Arrow_Left)
                self.Arrows.append(Movie_Arrow_Right)

        if self.param.prototype_arrow_up != None or self.param.prototype_arrow_down != None:
            for i in range(1, self.param.grid_size[0] + 1):
                Movie_Arrow_Left = self.object.generateObject("Movie2_Button_Up_" + str(i), self.param.prototype_arrow_up)
                Movie_Arrow_Right = self.object.generateObject("Movie2_Button_Down_" + str(i), self.param.prototype_arrow_down)
                Movie_Slot_Left = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(i) + '_' + str(0))
                Movie_Slot_right = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(i) + '_' + str(9))

                Position_Left = Movie_Slot_Left.getWorldPosition()
                Position_Right = Movie_Slot_right.getWorldPosition()
                node_left = Movie_Arrow_Left.getEntityNode()
                node_right = Movie_Arrow_Right.getEntityNode()

                MovieSlotsEntityNode.addChild(node_left)
                MovieSlotsEntityNode.addChild(node_right)
                node_left.setWorldPosition(Position_Left)
                node_right.setWorldPosition(Position_Right)

                self.Arrows.append(Movie_Arrow_Left)
                self.Arrows.append(Movie_Arrow_Right)

    def _setup_Board(self):
        MovieSlotsEntity = self.Movie_Slots_Start.getEntity()
        # MovieSlotsEntityNode = self.Movie_Slots_Start.getEntityNode()

        for i in range(1, self.param.grid_size[0] + 1):
            first = True
            last_Node = None
            for j in range(self.param.grid_size[1]):
                slotName = 'slot_' + str(i) + "_" + str(j)
                has_Movie_Slot = MovieSlotsEntity.hasMovieSlot(slotName)
                if has_Movie_Slot:
                    self.Board_State[i][j + 1] = "Block"
                    Block_Name = "Square_" + str(i) + "_" + str(j)
                    Movie_Block = self.object.generateObject(Block_Name, self.param.PrototypeBlock)
                    Movie_Slot = self.Movie_Slots_Start.getMovieSlot(slotName)

                    node = Movie_Block.getEntityNode()

                    Movie_Slot.addChild(node)

                    if first:
                        self.Blocks.append([Movie_Block])
                    else:
                        self.Blocks[i - 1].append(Movie_Block)
                    first = False

    def _setup_Chips(self):
        MovieSlotsEntityNode = self.Movie_Slots_Grid.getEntityNode()

        self.Board_State = [[None] * (self.param.grid_size[1] + 2) for i in range(self.param.grid_size[0] + 2)]

        for i in range(self.ChipNumber):
            self.Board_State[0][4 + 4 * i] = "Chip"
            self.Chip_State.append([0, 4 + 4 * i])
            ChipName = self.param.chips[i].prototype
            Chip = self.object.getObject(ChipName)
            Chip.setEnable(True)
            node = Chip.getEntityNode()

            Movie_Slot_Start = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(0) + '_' + str(self.param.chips[i].start))
            Movie_Slot_Finish = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(0) + '_' + str(self.param.chips[i].finish))

            Movie_Slot_Start.addChild(node)

            self.Finish.append(Movie_Slot_Finish.getWorldPosition())
            self.Chips.append(Chip)

    def _setup_distance(self):
        Movie_Slot_1 = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(1) + '_' + str(1))
        Movie_Slot_2 = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(2) + '_' + str(1))
        Movie_Slot_3 = self.Movie_Slots_Grid.getMovieSlot('slot_' + str(1) + '_' + str(2))
        pos_1 = Movie_Slot_1.getWorldPosition()
        pos_2 = Movie_Slot_2.getWorldPosition()
        pos_3 = Movie_Slot_3.getWorldPosition()

        self.One_Block_Hight = pos_2.y - pos_1.y
        self.One_Block_Width = pos_3.x - pos_1.x

    def _scopeMove_Chips(self, source, k):
        step = 0
        for i in range(len(self.Board_State)):
            for j in range(len(self.Board_State[i])):
                if self.Board_State[i][j] == "Chip":
                    if self.Chip_State[k][1] == j:
                        step = i - self.Chip_State[k][0]
                        self.Chip_State[k][0] = i
                        break
        if step == 0:
            return

        Chip = self.Chips[k]
        node = Chip.getEntityNode()
        pos_chip = node.getLocalPosition()
        posTo = (pos_chip.x, pos_chip.y + self.One_Block_Hight * step)
        speed = (self.speed) * (float(step) / 3)
        source.addTask("TaskNodeMoveTo", Node=node, To=posTo, Speed=speed)
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipGravitySlider_Move_Chip')
        pass

    def _Board_Chip_Move(self):
        # need optimisation
        for i in range(len(self.Board_State) - 1):
            for j in range(len(self.Board_State[i])):
                if self.Board_State[i][j] == "Chip" and self.Board_State[i + 1][j] != "Block":
                    self.Board_State[i + 1][j], self.Board_State[i][j] = self.Board_State[i][j], self.Board_State[i + 1][j]

                    self._Board_Chip_Move()
                    return

    def _Board_Block_Move(self, column, diraction):
        chip = 0
        chip_Index = []
        checker = []
        for i in range(len(self.Board_State[column + 1])):
            if self.Board_State[column + 1][i] == "Chip":
                chip_Index.append(i)
                chip += 1

        if chip == 0:
            self._Board_Block_Move_rec(column, diraction)
            return diraction
        else:
            return self._Board_Block_Move_Chip(column, chip_Index, diraction)

    def _Board_Block_Move_Chip(self, column, chip_Index, diraction):
        for i in range(len(chip_Index)):
            if self.Board_State[column + 1][chip_Index[i] + diraction] == "Block":
                return
        if diraction < 0 and self.Board_State[column + 1][-2] == "Block":
            return
        elif diraction > 0 and self.Board_State[column + 1][1] == "Block":
            return

        self._Board_Block_Move_Free(column, diraction)

        for i in range(len(chip_Index)):
            self.Board_State[column + 1][chip_Index[i]], self.Board_State[column + 1][chip_Index[i] - diraction] = \
                self.Board_State[column + 1][chip_Index[i] - diraction], self.Board_State[column + 1][chip_Index[i]]

        self._Board_Block_Move_Chip(column, chip_Index, diraction)

    def _Board_Block_Move_rec(self, column, diraction):
        if diraction < 0 and self.Board_State[column + 1][-2] == "Block":
            return None
        elif diraction > 0 and self.Board_State[column + 1][1] == "Block":
            return None
        else:
            self._Board_Block_Move_Free(column, diraction)
            self._Board_Block_Move_rec(column, diraction)

    def _Board_Block_Move_Free(self, column, diraction):
        if diraction > 0:
            for i in range(1, len(self.Board_State[column + 1]) - 1):
                self.Board_State[column + 1][i], self.Board_State[column + 1][i + 1] = \
                    self.Board_State[column + 1][i + 1], self.Board_State[column + 1][i]
        if diraction < 0:
            for i in range(len(self.Board_State[column + 1]) - 2, 1, -1):
                self.Board_State[column + 1][i], self.Board_State[column + 1][i - 1] = \
                    self.Board_State[column + 1][i - 1], self.Board_State[column + 1][i]

    def _scopeMove_Blocks(self, source, btn_holder):
        self._setup_distance()
        Button = btn_holder.get()

        step = 0
        index_arrow = self.Arrows.index(Button)
        diraction = index_arrow % 2
        column = index_arrow // 2

        Blocks_column = self.Blocks[column]
        Blocks_pos = []
        Blocks_nodes = []

        for i in range(len(self.Board_State[column + 1])):
            if self.Board_State[column + 1][i] == "Block":
                First_Block_Index = i
                break

        if diraction == 0:
            self._Board_Block_Move(column, 1)
        elif diraction == 1:
            self._Board_Block_Move(column, -1)
        elif diraction == 2:
            return
        elif diraction == 3:
            return
        else:
            return

        for i in range(len(self.Board_State[column + 1])):
            if self.Board_State[column + 1][i] == "Block":
                step = i - First_Block_Index
                # print step
                break

        if step == 0:
            return

        for block in Blocks_column:
            node = block.getEntityNode()
            posFrom = node.getLocalPosition()

            posTo = (posFrom.x + self.One_Block_Width * step, posFrom.y)
            Blocks_pos.append(posTo)
            Blocks_nodes.append(node)
        with source.addParallelTask(3) as (Tc_Sound_1, Tc_Sound_2, Tc_Game):
            Tc_Sound_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipGravitySlider_Move_Blocks')
            for ii, source_2 in Tc_Game.addParallelTaskList(range(len(Blocks_pos))):
                source_2.addTask("TaskNodeMoveTo", Node=Blocks_nodes[ii], To=Blocks_pos[ii], Speed=self.speed)
        source.addFunction(self._Board_Chip_Move)
        source.addFunction(self._Print_Board_State)

    def _Print_Board_State(self):
        pass

    def _IsGameEnd(self):
        if self.Board_State[-1][4] == "Chip" and self.Board_State[-1][8] == "Chip":
            self._Complete()
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
        self._playEnigma()

    def _Clean_Full(self):
        if self.tc is not None:
            self.tc.cancel()

        for elem in self.Blocks:
            for movie in elem:
                movie.onDestroy()

        for movie in self.Arrows:
            movie.onDestroy()

        for movie in self.Chips:
            node = movie.getEntityNode()
            node.removeFromParent()
            movie.setEnable(False)

        self.tc = None
        self.param = None
        self.Movie_Slots_Grid = None
        self.Movie_Slots_Start = None
        self.ChipNumber = None
        self.Chips = []
        self.Blocks = []
        self.Arrows = []
        self.Finish = []
        self.First_Block = []
        self.One_Block_Hight = 0
        self.One_Block_Width = 0
        self.Board_State = []
        self.Chip_State = []
        self.speed = 600.0

    def _onDeactivate(self):
        super(ChipGravitySlider, self)._onDeactivate()
        self._Clean_Full()
