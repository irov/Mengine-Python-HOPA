from Foundation.TaskManager import TaskManager

from HOPA.GlobeGameManager import GlobeGameManager


Enigma = Mengine.importEntity("Enigma")


class GlobeGame(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(GlobeGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def _onPreparation(self):
        super(Enigma, self)._onPreparation()
        self.PointsMovie = self.object.getObject("Movie_Points")
        self.PointsMovie.setEnable(False)
        pass

    def ReInitParamentrs(self):
        self.MovieNames = ("Movie_GRed", "Movie_GPurpl", "Movie_GYellow")

        self.Fields = [3, 4, 5, 4, 3]

        self.FieldSockets = []

        self.RotateCount = 7
        self.FieldsData = []  # [][]
        self.RotateData = []

        self.AllGlob = []
        self.FreeGlob = []

        self.PointsMovie = None
        self.RotateMovie = None

        # self.Lvl_1 = [[0,0,0], [1,1,1,1], [2,2,2,2,2], [1,1,1,1], [0,0,0]]
        # self.Lvl_Win = [[0,0,0], [1,1,1,1], [2,2,1,2,2], [1,0,1,2], [0,0,1]]
        self.Game = None
        self.Lvl_1 = None
        self.Lvl_Win = None

        self.Lvl_Movies = [[None, None, None], [None, None, None, None], [None, None, None, None, None],
            [None, None, None, None], [None, None, None]]
        self.Rotateble = [[False, False, False], [False, True, True, False], [False, True, True, True, False],
            [False, True, True, False], [False, False, False]]

        self.Click = None
        self.AfterRotate = []
        pass

    def _skipEnigma(self):
        self.enigmaComplete()
        self._stopppp()
        pass

    def _playEnigma(self):
        self.Pre_Init()

        self.FieldsData = self.Lvl_1

        self.__set_Points()
        self.__set_Aliasee()
        pass

    def Pre_Init(self):
        self.Game = GlobeGameManager.getGame(self.EnigmaName)
        self.Lvl_1 = self.Game.LvlStart
        self.Lvl_Win = self.Game.LvlWin

        self.RotateMovie = self.object.getObject("Movie_Rotate")

        count = self.RotateCount
        for l in self.Fields:
            count = count + l
            pass

        for i in range(len(self.MovieNames)):
            self.FreeGlob.append([])
            self.AllGlob.append([])
            pass

        for en, name in enumerate(self.MovieNames):
            for i in range(count):
                NameN = "%s%s" % (name, i)
                NameG = name
                movie = self.object.generateObject(NameN, NameG)
                movie.setPosition((0, 0))
                self.FreeGlob[en].append(movie)
                self.AllGlob[en].append(movie)

                movie.setEnable(False)
            pass

        pass

        pass

    def __set_Points(self):
        self.PointsMovie.setEnable(True)
        for y, lvD in enumerate(self.FieldsData):
            self.FieldSockets.append([])
            for x, val in enumerate(lvD):
                self.__Update_Point(x, y)
                pass
            pass
        self.PointsMovie.setEnable(False)
        pass

    def __Update_Point(self, x, y):
        nameSub = "p_%d_%d" % (y, x)
        Movie = self.PointsMovie.getEntity().getSubMovie(nameSub)

        pos = Movie.getLocalPosition()
        PosAnch = Movie.getOrigin()  # anchar
        Movie.disable()

        posnnn = (pos[0] - PosAnch[0], pos[1] - PosAnch[1])

        val = self.FieldsData[y][x]

        newMov = self.FreeGlob[val].pop()
        newMov.setPosition(posnnn)
        self.Lvl_Movies[y][x] = newMov
        newMov.setEnable(True)

        movieSock = self.object.generateObject("s_%d_%d" % (y, x), "Movie_sock")
        movieSock.setPosition(posnnn)
        self.FieldSockets[y].append(movieSock)
        pass

    def __set_Aliasee(self):
        for y, lvD in enumerate(self.FieldsData):
            for x, val in enumerate(lvD):
                self.__set_Aliae(x, y)
                pass
            pass

        def checkWin():
            for y, xxx in enumerate(self.FieldsData):
                for x, val in enumerate(xxx):
                    if (self.FieldsData[y][x] != self.Lvl_Win[y][x]):
                        return
                        pass
                    pass
                pass
            self._stopppp()
            self.enigmaComplete()
            pass

        with TaskManager.createTaskChain(Name="GlobeGame_Rotate", Repeat=True) as tc:
            tc.addListener(Notificator.onGlobeGameRotate)
            tc.addFunction(self._setRotate)
            tc.addTask("TaskMoviePlay", Movie=self.RotateMovie, Wait=True)
            tc.addFunction(self._endRotate)
            tc.addFunction(checkWin)
            pass

        pass

    def __set_Aliae(self, x, y):
        if (self.Rotateble[y][x] is False):
            return
            pass

        mov = self.FieldSockets[y][x]
        sockName = "socket"

        def cl():
            self.Click = (x, y)
            pass

        with TaskManager.createTaskChain(Name="GlobeGame_%d_%d" % (y, x), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=mov, isDown=True)
            tc.addFunction(cl)
            tc.addNotify(Notificator.onGlobeGameRotate)
            pass
        pass

    def _setRotate(self):
        x = self.Click[0]
        y = self.Click[1]
        if (y == 1):
            adT = (-1, 0)
            adD = (0, +1)
            pass
        elif (y == 2):
            adT = (-1, 0)
            adD = (-1, 0)
            pass
        else:  # (y == 4):
            adT = (0, +1)
            adD = (-1, 0)
            pass

        self._setRotateMov((x + adT[0], y - 1), (x + adT[1], y - 1), (0, 0))
        self._setRotateMov((x + adT[1], y - 1), (x + 1, y - 0), (0, 1))

        self._setRotateMov((x - 1, y - 0), (x + adT[0], y - 1), (1, 0))
        self._setRotateMov((x - 0, y - 0), (x - 0, y - 0), (1, 1))
        self._setRotateMov((x + 1, y - 0), (x + adD[1], y + 1), (1, 2))

        self._setRotateMov((x + adD[0], y + 1), (x - 1, y - 0), (2, 0))
        self._setRotateMov((x + adD[1], y + 1), (x + adD[0], y + 1), (2, 1))

        pos = self.FieldSockets[y][x].getPosition()
        posN = (pos[0] + 37, pos[1] + 35)
        self.RotateMovie.setPosition(posN)
        self.RotateMovie.setEnable(True)

        for ss in self.AfterRotate:
            pos = ss[0]
            val = ss[1]
            x = pos[0]
            y = pos[1]
            self.FieldsData[y][x] = val
            pass
        pass

    def _setRotateMov(self, b, t, m):
        x = b[0]
        y = b[1]

        slot = self.RotateMovie.getEntity().getMovieSlot("slot_%d_%d" % (m[0], m[1]))
        val = self.FieldsData[y][x]
        mov = self.FreeGlob[val].pop()
        mov.setEnable(True)

        self.RotateData.append((mov, val, mov.getEntity().getParent()))
        slot.addChild(mov.getEntity())
        self._ClearSlot(x, y)

        self.AfterRotate.append((t, val))
        pass

    def _endRotate(self):
        for mov in self.RotateData:
            move = mov[0]
            mEnt = move.getEntity()
            mov[2].addChild(mEnt)
            self.FreeGlob[mov[1]].append(move)
            pass
        self.RotateData = []
        self.RotateMovie.setEnable(False)

        for ss in self.AfterRotate:
            pos = ss[0]
            x = pos[0]
            y = pos[1]
            self._setMovieSlot(x, y)
            pass
        self.AfterRotate = []
        pass

    def _setMovieSlot(self, x, y):
        nameSub = "p_%d_%d" % (y, x)
        Movie = self.PointsMovie.getEntity().getSubMovie(nameSub)

        pos = Movie.getLocalPosition()
        PosAnch = Movie.getOrigin()  # anchar

        posnnn = (pos[0] - PosAnch[0], pos[1] - PosAnch[1])

        val = self.FieldsData[y][x]

        newMov = self.FreeGlob[val].pop()
        newMov.setPosition(posnnn)
        self.Lvl_Movies[y][x] = newMov
        newMov.setEnable(True)
        pass

    def _ClearSlot(self, x, y):
        val = self.FieldsData[y][x]
        mov = self.Lvl_Movies[y][x]
        if (mov is not None):
            mov.setEnable(False)
            mov.setPosition((0, 0))
            self.FreeGlob[val].append(mov)
            pass
        pass

    def _stopEnigma(self):
        pass

    def _stopppp(self):
        for y, lvD in enumerate(self.FieldsData):
            for x, val in enumerate(lvD):
                name = "GlobeGame_%d_%d" % (y, x)
                if TaskManager.existTaskChain(name) is True:
                    TaskManager.cancelTaskChain(name)
                    pass
                mov = self.Lvl_Movies[y][x]
                if (mov is not None):
                    mov.removeFromParent()
                    pass
                pass
            pass

        if TaskManager.existTaskChain("GlobeGame_Rotate") is True:
            TaskManager.cancelTaskChain("GlobeGame_Rotate")
            pass

        if TaskManager.existTaskChain("GlobeGame_Rotate") is True:
            TaskManager.cancelTaskChain("GlobeGame_Rotate")
            pass

        self.ReInitParamentrs()
        pass

    pass
