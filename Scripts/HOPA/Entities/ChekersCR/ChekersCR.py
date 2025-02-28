from Foundation.TaskManager import TaskManager


Enigma = Mengine.importEntity("Enigma")


class ChekersCR(Enigma):
    Cell_None = 0
    Cell_Idle = 1
    Cell_Select = 2
    Cell_Move_To = 3

    Cell_Move_T = 4
    Cell_Move_D = 5
    Cell_Move_L = 6
    Cell_Move_R = 7
    Cell_Eat = 8

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(ChekersCR, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Field_Len_X = 7
        self.Field_Len_Y = 7

        self.Movie_Points = None

        self.Movie_Move_T = None
        self.Movie_Move_D = None
        self.Movie_Move_L = None
        self.Movie_Move_R = None

        self.Movie_Select = None
        self.Movie_Move_To = None
        self.Movie_Idle = None
        self.Movie_None = None

        self.Field = [[0 for col in range(self.Field_Len_X)] for row in range(self.Field_Len_Y)]
        self.Field_Movies = [[None for col in range(self.Field_Len_X)] for row in range(self.Field_Len_Y)]
        self.AliasNames = []

        self.Click = None
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self.__PreInit()
        self.__Init()
        pass

    def __PreInit(self):
        self.Movie_Points = self.object.getObject("Movie_Points")

        self.Movie_Move_T = "Movie_B_Move_T"
        self.Movie_Move_D = "Movie_B_Move_D"
        self.Movie_Move_L = "Movie_B_Move_L"
        self.Movie_Move_R = "Movie_B_Move_R"
        self.Movie_Eat = "Movie_B_Eat"

        self.Movie_Select = "Movie_B_Active"
        self.Movie_Move_To = "Movie_B_Move_Cell"
        self.Movie_Idle = "Movie_B_Idle"
        self.Movie_None = "Movie_B_None"

        self.Field = [[0 for col in range(self.Field_Len_X)] for row in range(self.Field_Len_Y)]
        self.Field_Movies = [[None for col in range(self.Field_Len_X)] for row in range(self.Field_Len_Y)]
        self.AliasNames = []

        self.Click = None

        self.Move_To_Click = None
        self.Move_From_Click = None
        self.Move_Eat_Click = None

        self.Move_Status = 3
        pass

    def __Init(self):
        self.__StartGame()
        pass

    def __StartGame(self):
        self.__Finita()
        self.Field = [[0 for col in range(self.Field_Len_X)] for row in range(self.Field_Len_Y)]
        for x in range(self.Field_Len_X):
            for y in range(self.Field_Len_Y):
                self.__ReInit_Cell(x, y, 0)
                pass
        ##############################################
        for x in range(3):
            for y in range(3):
                self.__ReInit_Cell(x + 2, y + 2, 1)
                pass
            pass

        self.__ReInit_Cell(1, 3, 1)
        self.__ReInit_Cell(3, 1, 1)
        self.__ReInit_Cell(3, 5, 1)
        self.__ReInit_Cell(5, 3, 1)

        self.__Do_Aliases()
        pass

    def __Do_Aliases(self):
        for x in range(self.Field_Len_X):
            for y in range(self.Field_Len_Y):
                self.__Do_Alias(x, y)
                pass
            pass

        self.__Do_Alias_Restart()
        pass

    def __Do_Alias(self, x, y):
        mov_Play = [[(None, True)]]

        xp = x
        yp = y

        def rea():
            if (self.Move_Eat_Click != None):
                x_in = self.Move_Eat_Click[0]
                y_in = self.Move_Eat_Click[1]
                if (x_in == xp and y_in == yp):
                    if (self.Move_Status == 3):
                        self.__ReInit_Cell(x, y, ChekersCR.Cell_None)
                        self.Move_Eat_Click = None
                        pass
                    pass
                pass

            if (self.Move_To_Click != None):
                x_in = self.Move_To_Click[0]
                y_in = self.Move_To_Click[1]
                if (x_in == x and y_in == y):
                    if (self.Move_Status == 3):
                        self.__ReInit_Cell(x, y, ChekersCR.Cell_Idle)
                        self.Move_To_Click = None

                        fc = 0
                        for x1 in range(self.Field_Len_X):
                            for y1 in range(self.Field_Len_Y):
                                v = self.Field[x1][y1]
                                if (v == ChekersCR.Cell_Idle):
                                    fc = fc + 1
                                    pass
                                pass
                            pass

                        if (fc == 1):
                            self.__Finita()
                            self.enigmaComplete()
                            pass
                        pass
                    pass
                pass

            if (self.Move_From_Click != None):
                x_in = self.Move_From_Click[0]
                y_in = self.Move_From_Click[1]
                if (x_in == xp and y_in == yp):
                    if (self.Move_Status == 1):
                        self.__Skip_Mov(self.Move_To_Click[0], self.Move_To_Click[1])
                        self.__Skip_Mov(self.Move_Eat_Click[0], self.Move_Eat_Click[1])
                        self.Move_Status = 2
                        pass
                    else:
                        self.__ReInit_Cell(x, y, ChekersCR.Cell_None)
                        self.Move_From_Click = None
                        self.Move_Status = 3
                        pass

                    pass
                pass
            mov = self.Field_Movies[xp][yp]
            mov_Play[0] = [(mov, True)]
            pass

        def Click():
            if (self.Move_Status != 3):
                return
                pass

            val = self.Field[x][y]
            if (self.Click != None):
                self.__tryRemoveMoveClick()
                if (val != ChekersCR.Cell_Move_To):
                    self.__ReInit_Cell(self.Click[0], self.Click[1], ChekersCR.Cell_Idle)
                    pass
                else:
                    x_c = self.Click[0]
                    y_c = self.Click[1]
                    dif_x = x_c - x
                    dif_y = y_c - y
                    xpa = x
                    ypa = y
                    if (dif_x != 0):
                        xpa = xpa + dif_x / 2
                        if (dif_x > 0):
                            val = ChekersCR.Cell_Move_L
                            pass
                        else:
                            val = ChekersCR.Cell_Move_R
                            pass
                        pass
                    else:
                        if (dif_y != 0):
                            ypa = ypa + dif_y / 2
                            if (dif_y > 0):
                                val = ChekersCR.Cell_Move_T
                                pass
                            else:
                                val = ChekersCR.Cell_Move_D
                                pass
                            pass
                        pass

                    self.Move_Status = 1
                    self.Move_To_Click = (x, y)
                    self.Move_From_Click = self.Click
                    self.Move_Eat_Click = (xpa, ypa)

                    self.__ReInit_Cell(x, y, ChekersCR.Cell_None)
                    self.__ReInit_Cell(xpa, ypa, ChekersCR.Cell_Eat)
                    self.__ReInit_Cell(self.Click[0], self.Click[1], val)

                    pass
                self.Click = None
                return
                pass

            self.Click = None
            if (val != 1):
                return
                pass

            self.Click = (x, y)
            self.__ReInit_Cell(x, y, ChekersCR.Cell_Select)
            self.__tryAddMoveClick()
            pass

        name_A1 = "Cell_Idle_%d_%d" % (x, y)
        name_A2 = "Cell_Click_%d_%d" % (x, y)
        self.AliasNames.append(name_A1)
        self.AliasNames.append(name_A2)

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addFunction(rea)
            tc.addTask("AliasMultyplMovePlay", Movies=mov_Play)
            pass

        sockName = "socket_%d_%d" % (x + 1, y + 1)

        with TaskManager.createTaskChain(Name=name_A2, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=self.Movie_Points)
            tc.addFunction(Click)
            pass
        pass

    def __Do_Alias_Restart(self):
        name_A1 = "Restart %s" % (self.EnigmaName)
        self.AliasNames.append(name_A1)

        with TaskManager.createTaskChain(Name=name_A1) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName="Reset", Movie=self.Movie_Points)
            tc.addPrint("restart ")
            tc.addFunction(self.__Restart)
            pass
        pass

    #
    def __tryAddMoveClick(self):
        x = self.Click[0]
        y = self.Click[1]
        self.__tryAddMove((x + 1, y), (x + 2, y))
        self.__tryAddMove((x - 1, y), (x - 2, y))
        self.__tryAddMove((x, y + 1), (x, y + 2))
        self.__tryAddMove((x, y - 1), (x, y - 2))
        pass

    def __tryRemoveMoveClick(self):
        x = self.Click[0]
        y = self.Click[1]
        self.__tryRemoveMove((x + 1, y), (x + 2, y))
        self.__tryRemoveMove((x - 1, y), (x - 2, y))
        self.__tryRemoveMove((x, y + 1), (x, y + 2))
        self.__tryRemoveMove((x, y - 1), (x, y - 2))
        pass

    def __tryAddMove(self, point_1, point_2):
        if (self.__Check_Range(point_1) is False):
            return
            pass

        if (self.__Check_Range(point_2) is False):
            return
            pass
        val1 = self.Field[point_1[0]][point_1[1]]
        val2 = self.Field[point_2[0]][point_2[1]]
        if (val1 != ChekersCR.Cell_Idle or val2 != ChekersCR.Cell_None):
            return
            pass

        self.__ReInit_Cell(point_2[0], point_2[1], ChekersCR.Cell_Move_To)
        pass

    def __tryRemoveMove(self, point_1, point_2):
        if (self.__Check_Range(point_1) is False):
            return
            pass

        if (self.__Check_Range(point_2) is False):
            return
            pass
        val1 = self.Field[point_1[0]][point_1[1]]
        val2 = self.Field[point_2[0]][point_2[1]]
        if (val2 != ChekersCR.Cell_Move_To):
            return
            pass

        self.__ReInit_Cell(point_2[0], point_2[1], ChekersCR.Cell_None)
        pass

    def __Check_Range(self, point):
        if (point[0] >= self.Field_Len_X or point[0] < 0 or point[1] >= self.Field_Len_Y or point[1] < 0):
            return False
        return True
        pass

    def __ReInit_Cell(self, x, y, val):
        self.Field[x][y] = val

        movOld = self.Field_Movies[x][y]

        mov = self.gen_Mov(x, y, val)
        self.Field_Movies[x][y] = mov

        if (movOld != None):
            self.__Skip_Movie(movOld)
            movOld.getEntity().removeFromParent()
            pass
        pass

    def __Skip_Mov(self, x, y):
        mov = self.Field_Movies[x][y]
        self.__Skip_Movie(mov)
        pass

    def gen_Mov(self, x, y, val):
        if (val == ChekersCR.Cell_None):
            movName = self.Movie_None
            pass
        elif (val == ChekersCR.Cell_Idle):
            movName = self.Movie_Idle
            pass
        elif (val == ChekersCR.Cell_Select):
            movName = self.Movie_Select
            pass
        elif (val == ChekersCR.Cell_Move_To):
            movName = self.Movie_Move_To
            pass
        elif (val == ChekersCR.Cell_Move_T):
            movName = self.Movie_Move_T
            pass
        elif (val == ChekersCR.Cell_Move_D):
            movName = self.Movie_Move_D
            pass
        elif (val == ChekersCR.Cell_Move_L):
            movName = self.Movie_Move_L
            pass
        elif (val == ChekersCR.Cell_Move_R):
            movName = self.Movie_Move_R
            pass
        else:
            movName = self.Movie_Eat
            pass
        mov = self.object.generateObject("%s_%d_%d" % (movName, x, y), movName)
        mov.setPosition((0, 0))
        self.__Attach_Movie(x, y, mov)

        return mov
        pass

    def __End_Movie(self, x, y):
        mov = self.Field_Movies[x][y]
        if (mov is None):
            return
            pass

        self.__Skip_Movie(mov)
        mov.getEntity().removeFromParent()
        pass

    def __Attach_Movie(self, x, y, mov):
        MovieSlotPointsEntity = self.Movie_Points.getEntity()
        id = "slot_%d_%d" % (x + 1, y + 1)
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)
        CurrentSlot.addChild(mov.getEntity())
        pass

    def __Skip_Movie(self, mov):
        if (mov is None):
            return
            pass
        mov_Ent = mov.getEntity()
        dur = mov.getDuration() * 999
        mov_Ent.setTiming(dur)
        pass

    def __EndGame(self):
        for x in range(self.Field_Len_X):
            for y in range(self.Field_Len_Y):
                movOld = self.Field_Movies[x][y]

                if (movOld != None):
                    self.__Skip_Movie(movOld)
                    movOld.getEntity().removeFromParent()
                    pass
                pass

        for an in self.AliasNames:
            self.__canTT(an)
            pass
        self.AliasNames = []
        pass

    def __Restart(self):
        self.__EndGame()
        self.__PreInit()
        self.__StartGame()
        pass

    def __Finita(self):
        self.__EndGame()
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass
