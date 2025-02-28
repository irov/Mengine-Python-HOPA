from Foundation.TaskManager import TaskManager
from HOPA.PetnaGameManager import PetnaGameManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")

import math


class PetnaGame(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(PetnaGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Game = None
        self.FieldWidth = None
        self.FieldHeight = None
        self.FieldData = None
        self.FieldMoviesIdle = []
        self.FieldMoviesUnd = []
        self.moveeIdle = []

        self.Movies = []
        self.MoviesUnd = []
        self.Movie_Points = None

        self.Movie_Move_Ar = []
        self.Movie_Move_T = None
        self.Movie_Move_D = None
        self.Movie_Move_L = None
        self.Movie_Move_R = None

        self.Movie_Move_TL = None
        self.Movie_Move_TR = None
        self.Movie_Move_DL = None
        self.Movie_Move_DR = None

        self.Selected = (-1, -1)
        self.Selected2 = (-1, -1)
        self.MoveMoviesPlay = [[(None, True)]]
        self.ClickDisable = False
        self.Und = False
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
        self.Game = PetnaGameManager.getGame(self.EnigmaName)
        self.FieldWidth = self.Game.FieldWidth
        self.FieldHeight = self.Game.FieldHeight
        self.FieldData = self.Game.StartData
        pass

    def __Init(self):
        self.Movie_Points = self.object.getObject("Movie_Points")

        self.Movie_Move_T = self.object.getObject("Movie_Move_T")
        self.Movie_Move_D = self.object.getObject("Movie_Move_D")
        self.Movie_Move_L = self.object.getObject("Movie_Move_L")
        self.Movie_Move_R = self.object.getObject("Movie_Move_R")

        self.Movie_Move_TL = self.object.getObject("Movie_Move_TL")
        self.Movie_Move_TR = self.object.getObject("Movie_Move_TR")
        self.Movie_Move_DL = self.object.getObject("Movie_Move_DL")
        self.Movie_Move_DR = self.object.getObject("Movie_Move_DR")

        self.Movie_Move_Ar.append([])
        self.Movie_Move_Ar.append([])
        self.Movie_Move_Ar.append([])

        self.Movie_Move_Ar[0].append(self.Movie_Move_TL)
        self.Movie_Move_Ar[0].append(self.Movie_Move_T)
        self.Movie_Move_Ar[0].append(self.Movie_Move_TR)

        self.Movie_Move_Ar[1].append(self.Movie_Move_L)
        self.Movie_Move_Ar[1].append(None)
        self.Movie_Move_Ar[1].append(self.Movie_Move_R)

        self.Movie_Move_Ar[2].append(self.Movie_Move_DL)
        self.Movie_Move_Ar[2].append(self.Movie_Move_D)
        self.Movie_Move_Ar[2].append(self.Movie_Move_DR)

        for y in range(self.FieldHeight):
            for x in range(self.FieldWidth):
                id = x + y * self.FieldWidth + 1
                name = "Movie_Cell_%d" % (id)
                nameUnd = "Movie_CellUnd_%d" % (id)
                movie = self.object.getObject(name)
                movieUnd = self.object.getObject(nameUnd)

                self.Movies.append(movie)
                self.MoviesUnd.append(movieUnd)
                movieUnd.setEnable(False)

                self.FieldMoviesIdle.append(None)
                self.FieldMoviesUnd.append(None)
                self.moveeIdle.append([])
                pass
            pass

        self.__InitField()

        self.__InitAlias()
        pass

    def __InitField(self):
        for y in range(self.FieldHeight):
            for x in range(self.FieldWidth):
                self.__setMovie(x, y)
                pass
            pass

    def __InitAlias(self):
        for y in range(self.FieldHeight):
            for x in range(self.FieldWidth):
                self.__set_Alias(x, y)
                pass
            pass

        def afterPlay():
            self.MoveMoviesPlay[0] = [(None, True)]
            self.ClickDisable = False

            self.__setMovie(self.Selected[0], self.Selected[1])
            self.__setMovie(self.Selected2[0], self.Selected2[1])

            self.Selected = (-1, -1)
            self.Selected2 = (-1, -1)
            self._CheckWin()
            pass

        with TaskManager.createTaskChain(Name="PetnaGamePlayMove", Repeat=True) as tc:
            tc.addListener(Notificator.onPetnaSwap)
            tc.addTask("AliasMultyplMovePlay", Movies=self.MoveMoviesPlay)
            tc.addFunction(afterPlay)
            pass
        pass

    def __set_Alias(self, x, y):
        sockName = "socket_%s_%s" % (y + 1, x + 1)
        id_Movie = self.__getMovieId(x, y)

        movIdl = [self.FieldMoviesIdle[id_Movie]]
        movAc = [self.FieldMoviesUnd[id_Movie]]

        self.moveeIdle[id_Movie] = [[(movIdl[0], True)]]

        def funClick():
            movIdl[0] = self.FieldMoviesIdle[id_Movie]
            movAc[0] = self.FieldMoviesUnd[id_Movie]

            setMovieIdleActive()
            if (self.Selected[0] != -1):
                disX = self.Selected[0] - x
                disY = self.Selected[1] - y
                dxA = math.fabs(disX)
                dyA = math.fabs(disY)
                if ((disX == 0 and disY == 0) or dxA > 1 or dyA > 1):
                    #####################
                    id_sel = self.__getMovieId(self.Selected[0], self.Selected[1])
                    mISel = self.FieldMoviesIdle[id_sel]
                    mASel = self.FieldMoviesUnd[id_sel]

                    mASel.setEnable(False)
                    mISel.setEnable(True)

                    self.moveeIdle[id_sel][0] = [(mISel, True)]
                    #####################

                    self.Selected = (-1, -1)
                    setMovieIdle()
                    pass
                else:
                    # self.Und = False

                    self.Selected2 = (x, y)
                    m1 = movIdl[0]
                    m2 = movAc[0]
                    movIdl[0] = m2
                    movAc[0] = m1

                    self.__Swap(self.Selected[0], self.Selected[1], self.Selected2[0], self.Selected2[1])

                    self.ClickDisable = True
                    Notification.notify(Notificator.onPetnaSwap)
                    pass
                pass
            else:
                self.Selected = (x, y)
                pass
            pass

        def filter1():
            if (self.ClickDisable is True):
                return False
                pass
            return True
            pass

        def filter2():
            if (filter1() is False):
                return False
                pass

            if (self.Selected[0] == x and self.Selected[1] == y):
                return False
            return True
            pass

        with TaskManager.createTaskChain(Name="PetnaGame_%d_%d" % (y, x), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=self.Movie_Points, isDown=True,
                       Filter=filter1)
            tc.addFunction(funClick)
            pass

        def und():
            # self.Und = True
            movIdl[0] = self.FieldMoviesIdle[id_Movie]
            movAc[0] = self.FieldMoviesUnd[id_Movie]

            setMovieIdleActive()
            pass

        def undEnd():
            # print x, " leav ", y
            # un = self.Und
            # self.Und = False
            # if(un is False):
            #     print "ret 1"
            #     return
            #     pass
            if (filter2() is False):
                # print "ret 2"
                return
                pass
            setMovieIdle()
            pass

        def setMovieIdle():
            movAc[0].setEnable(False)
            movIdl[0].setEnable(True)

            self.moveeIdle[id_Movie][0] = [(movIdl[0], True)]
            pass

        def setMovieIdleActive():
            movIdl[0].setEnable(False)
            movAc[0].setEnable(True)
            self.moveeIdle[id_Movie][0] = [(movAc[0], True)]
            pass

        with TaskManager.createTaskChain(Name="PetnaGameUnder_%d_%d" % (y, x), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketEnter", SocketName=sockName, Movie=self.Movie_Points, Filter=filter2)
            tc.addFunction(und)
            tc.addTask("TaskMovieSocketLeave", SocketName=sockName, Movie=self.Movie_Points)
            tc.addFunction(undEnd)
            pass

        with TaskManager.createTaskChain(Name="PetnaGameIdle_%d_%d" % (y, x), Repeat=True) as tc:
            tc.addTask("AliasMultyplMovePlay", Movies=self.moveeIdle[id_Movie])
            pass
        pass

    def __Swap(self, x1, y1, x2, y2):
        id1 = self.__getMovieId(x1, y1)
        id2 = self.__getMovieId(x2, y2)
        val1 = self.FieldData[y1][x1]
        val2 = self.FieldData[y2][x2]
        self.FieldData[y1][x1] = val2
        self.FieldData[y2][x2] = val1

        mov1 = self.FieldMoviesIdle[id1]
        mov2 = self.FieldMoviesIdle[id2]
        mov1.setEnable(False)
        mov2.setEnable(False)

        mov1U = self.FieldMoviesUnd[id1]
        mov2U = self.FieldMoviesUnd[id2]
        mov1U.setEnable(True)
        mov2U.setEnable(True)

        difx1 = x1 - x2 + 1
        dify1 = y1 - y2 + 1
        difx2 = x2 - x1 + 1
        dify2 = y2 - y1 + 1

        movSlots2 = self.Movie_Move_Ar[dify1][difx1]
        movSlots1 = self.Movie_Move_Ar[dify2][difx2]
        slot1 = movSlots1.getEntity().getMovieSlot("slot")
        slot2 = movSlots2.getEntity().getMovieSlot("slot")

        slot1.addChild(mov1U.getEntity())
        slot2.addChild(mov2U.getEntity())

        slotf1 = self.Movie_Points.getEntity().getMovieSlot("slot_%d_%d" % (y1 + 1, x1 + 1))
        slotf2 = self.Movie_Points.getEntity().getMovieSlot("slot_%d_%d" % (y2 + 1, x2 + 1))

        slotf1.addChild(slot1)
        slotf2.addChild(slot2)

        self.MoveMoviesPlay[0] = [[movSlots1, False], [movSlots2, True]]
        pass

    def __setMovie(self, xm, ym):
        cellId = self.FieldData[ym][xm]
        cellId = cellId - 1
        slotName = "slot_%d_%d" % (ym + 1, xm + 1)
        slot = self.Movie_Points.getEntity().getMovieSlot(slotName)
        mov = self.Movies[cellId]
        movUnd = self.MoviesUnd[cellId]
        slot.addChild(mov.getEntity())
        slot.addChild(movUnd.getEntity())
        # print "%s %s %s %s" % (slot.getLocalPosition(), slot.getWorldPosition(), xm, ym)
        # # print "!!!!!!!!!!!!!!!!!!!!!!!"getOrigin getLocalPosition getCoordinate getWorldPosition
        # # for attr in dir(slot):
        # #     print "obj.%s = %s" % (attr, getattr(slot, attr))
        # # print "$$$$$$$$$$$$$$$$$$$$$$$$"
        mov.setEnable(True)
        movUnd.setEnable(False)

        id_Movie = self.__getMovieId(xm, ym)

        self.FieldMoviesIdle[id_Movie] = mov
        self.FieldMoviesUnd[id_Movie] = movUnd
        pass

    def __getMovieId(self, xm, ym):
        id = xm + ym * self.FieldWidth
        return id
        pass

    def _CheckWin(self):
        id = 0
        for y in range(self.FieldHeight):
            for x in range(self.FieldWidth):
                id = id + 1
                val = self.FieldData[y][x]
                if (id != val):
                    return
                    pass
                pass
            pass
        self.__Finita()
        self.enigmaComplete()
        pass

    def __Finita(self):
        for y in range(self.FieldHeight):
            for x in range(self.FieldWidth):
                self.__canTT("PetnaGame_%d_%d" % (y, x))
                self.__canTT("PetnaGameUnder_%d_%d" % (y, x))
                self.__canTT("PetnaGameIdle_%d_%d" % (y, x))
                id_Movie = self.__getMovieId(x, y)

                self.FieldMoviesIdle[id_Movie].setEnable(False)
                self.FieldMoviesUnd[id_Movie].setEnable(False)
                pass
            pass

        self.__canTT("PetnaGamePlayMove")
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass
