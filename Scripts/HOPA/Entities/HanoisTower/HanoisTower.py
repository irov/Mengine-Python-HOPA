from Foundation.TaskManager import TaskManager


Enigma = Mengine.importEntity("Enigma")


class HanoisTower(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(HanoisTower, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Movie_Points = None

        self.Movies_Pillons = []
        self.Movies_UP = []
        self.Movies_Down = []

        self.Pilars = []
        self.Pilars.append([])
        self.Pilars.append([])
        self.Pilars.append([])

        self.Click = -1
        self.PickValue = -1
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self._PreInit()
        self._Init()
        self._InitAlias()
        pass

    def _PreInit(self):
        self.Movie_Points = self.object.getObject("Movie_Points")

        self.Pilars[0].append(5)
        self.Pilars[0].append(4)
        self.Pilars[0].append(3)
        self.Pilars[0].append(2)
        self.Pilars[0].append(1)

        for i in range(5):
            name = "Movie_D%d" % (5 - i)
            mov = self.object.getObject(name)
            # mov = self.object.generateObject(name, name)
            self.Movies_Pillons.append(mov)
            mov.setEnable(True)

            pass
        for x in range(3):
            self.Movies_UP.append([])
            self.Movies_Down.append([])

            for i in range(5):
                name = "Movie_DUP_%d_%d" % (i + 1, x + 1)
                nameD = "Movie_DD_%d_%d" % (i + 1, x + 1)
                movUp = self.object.getObject(name)
                movDown = self.object.getObject(nameD)
                self.Movies_UP[x].append(movUp)
                self.Movies_Down[x].append(movDown)
                pass
            pass
        pass

    def _Init(self):
        for y, p1 in enumerate(self.Pilars[0]):
            self.__setDisk(1, y, p1)
            pass
        pass

    def _InitAlias(self):
        for i in range(3):
            self.__set_Aliae(i)
            pass

        self.Mov = [None]
        self.Clicked_1 = -1
        self.Clicked_2 = -1

        def filter():
            size = len(self.Pilars[self.Click])
            if (size == 0):
                return False
            return True
            pass

        def filter2():
            if (len(self.Pilars[self.Click]) == 0):
                return True
                pass
            val = self.Pilars[self.Click][-1]
            if (val > self.PickValue):
                return True
                pass
            return False
            pass

        self.parrent = None
        self.mm = None

        def set_Mov():
            self.Clicked_1 = self.Click
            size = len(self.Pilars[self.Clicked_1])
            mov = self.Movies_UP[self.Clicked_1][size - 1]
            slot = mov.getEntity().getMovieSlot("slot")

            self.Mov[0] = [[mov, True]]
            ##############################################
            val = self.Pilars[self.Click].pop()

            self.mm = self.Movies_Pillons[val - 1]
            self.mm.setPosition((0, 0))
            self.parrent = self.mm.getEntity().getParent()

            slot.addChild(self.mm.getEntity())

            self.PickValue = val
            pass

        def set_Mov_2():
            self.Clicked_2 = self.Click
            if (self.Clicked_2 == self.Clicked_1):
                self.Mov[0] = [[None, False]]
                return
                pass

            mov_Move = self.object.getObject("Movie_DM_%d_%d" % (self.Clicked_1 + 1, self.Clicked_2 + 1))
            slot_Move = mov_Move.getEntity().getMovieSlot("slot")
            slot_Move.addChild(self.mm.getEntity())

            self.Mov[0] = [[mov_Move, True]]
            pass

        def set_Mov_3():
            size = len(self.Pilars[self.Clicked_2])
            mov = self.Movies_Down[self.Clicked_2][size]
            slot = mov.getEntity().getMovieSlot("slot")
            slot.addChild(self.mm.getEntity())

            self.Mov[0] = [[mov, True]]
            pass

        def end_Mov():
            self.__AddDisk(self.Clicked_2, self.PickValue)
            self.parrent.addChildFront(self.mm.getEntity())
            pass

        with TaskManager.createTaskChain(Name="HanoisTowerPick", Repeat=True) as tc:
            tc.addListener(Notificator.onHanoisTowerClick, Filter=filter)

            tc.addFunction(set_Mov)
            tc.addTask("AliasMultyplMovePlay", Movies=self.Mov)

            tc.addListener(Notificator.onHanoisTowerClick, Filter=filter2)

            tc.addFunction(set_Mov_2)
            tc.addTask("AliasMultyplMovePlay", Movies=self.Mov)

            tc.addFunction(set_Mov_3)
            tc.addTask("AliasMultyplMovePlay", Movies=self.Mov)
            tc.addFunction(end_Mov)

            tc.addFunction(self.__CheckFin)
            pass
        pass

    def __AddDisk(self, x, val):
        size = len(self.Pilars[x])
        self.Pilars[x].append(val)
        self.__setDisk(x + 1, size, val)
        pass

    def __setDisk(self, x, y, val):
        nameSub = "D_%d_%d" % (y, x)
        Movie = self.Movie_Points.getEntity().getSubMovie(nameSub)
        pos = Movie.getLocalPosition()
        PosAnch = Movie.getOrigin()  # anchar

        posnnn = (pos[0] - PosAnch[0], pos[1] - PosAnch[1])
        self.Movies_Pillons[val - 1].setPosition(posnnn)
        pass

    def __set_Aliae(self, x):
        sockName = "socket_%d" % (x + 1)

        def set_Click():
            self.Click = x
            pass

        with TaskManager.createTaskChain(Name="HanoisTower_%d" % (x), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=self.Movie_Points, isDown=True)
            tc.addFunction(set_Click)
            tc.addNotify(Notificator.onHanoisTowerClick)
            pass
        pass

    def __CheckFin(self):
        if (len(self.Pilars[2]) == 5):
            self.__Finita()
            self.enigmaComplete()
            pass

        pass

    def __Finita(self):
        for i in range(3):
            if TaskManager.existTaskChain("HanoisTower_%d" % (i)) is True:
                TaskManager.cancelTaskChain("HanoisTower_%d" % (i))
                pass
            pass

        if TaskManager.existTaskChain("HanoisTowerPick") is True:
            TaskManager.cancelTaskChain("HanoisTowerPick")
            pass

        self.ReInitParamentrs()
        pass

    pass
