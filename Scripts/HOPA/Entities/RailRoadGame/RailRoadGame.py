from Foundation.TaskManager import TaskManager

from HOPA.RailRoadGameManager import RailRoadGameManager


Enigma = Mengine.importEntity("Enigma")


class RailRoadGame(Enigma):
    class InterDataSide():
        def __init__(self, Game, ManagerData):
            self.Game = Game
            self.ManagerData = ManagerData

            self.Disable = True

            self.MovieIdle = None
            self.MovieRotate = None
            self.MovieUnderMouse = None
            self.Id = self.ManagerData.Id

            self.Init()
            pass

        def Init(self):
            MovieIdleName = self.ManagerData.MovieIdle
            if (MovieIdleName is None):
                return
                pass

            self.Disable = False

            MovieRotateName = self.ManagerData.MovieRotate
            MovieUnderMouseName = self.ManagerData.MovieUnderMouse
            Slot = self.ManagerData.Slot

            self.MovieIdle = self.Game.object.generateObject("%s %s" % (MovieIdleName, self.Id), MovieIdleName)
            self.MovieRotate = self.Game.object.generateObject("%s %s" % (MovieRotateName, self.Id), MovieRotateName)
            self.MovieUnderMouse = self.Game.object.generateObject("%s %s" % (MovieUnderMouseName, self.Id), MovieUnderMouseName)

            slot = self.Game.Movie_Points.getEntity().getMovieSlot(Slot)
            slot.addChild(self.MovieIdle.getEntity())
            slot.addChild(self.MovieRotate.getEntity())
            slot.addChild(self.MovieUnderMouse.getEntity())

            self.DisableThis()
            pass

        def DisableThis(self):
            if (self.MovieIdle is None):
                return
                pass

            self.MovieIdle.setEnable(False)
            self.MovieRotate.setEnable(False)
            self.MovieUnderMouse.setEnable(False)
            pass

        pass

    class InterData():
        def __init__(self, Game, key):
            self.Key = key
            self.Game = Game
            self.ManagerDatas = []
            self.Value = 0
            pass

        def addData(self, ManagerData):
            dat = RailRoadGame.InterDataSide(self.Game, ManagerData)
            self.ManagerDatas.append(dat)
            pass

        def DoAliase(self):
            dat = self.ManagerDatas[self.Value]
            if (dat.Disable is True):
                return
                pass

            datAA = [dat]

            id = int(self.Key)

            name = "RailRoadGame%d" % (id)
            sockeName = "socket_%d" % (id)
            movI = dat.MovieIdle
            movI.setEnable(True)

            movv = [[(None, True)]]
            movvRotate = [[(None, True)]]
            click = [False]

            def und():
                click[0] = False
                movU = datAA[0].MovieUnderMouse
                movU.setEnable(True)
                movv[0] = [(movU, True)]
                movvRotate[0] = [(None, True)]
                datAA[0].MovieIdle.setEnable(False)
                pass

            def Click():
                click[0] = True
                mov = datAA[0].MovieRotate
                mov.setEnable(True)
                movvRotate[0] = [(mov, True)]

                pass

            def undLeav():
                datAA[0].MovieUnderMouse.setEnable(False)
                pass

            def RotateEnd():
                if (click[0] is True):
                    datAA[0].DisableThis()
                    self.Value = self.Value + 1
                    if (self.Value >= len(self.ManagerDatas)):
                        self.Value = 0
                        pass
                    datAA[0] = self.ManagerDatas[self.Value]
                    pass

                datAA[0].MovieIdle.setEnable(True)
                hp = self.Game.Movie_Points.getEntity().getSocket(sockeName)
                hp.disable()
                hp.enable()
                pass

            def fil():
                if (self.Game.PlayMovie is True):
                    return False
                    pass
                return True
                pass

            with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
                tc.addTask("TaskMovieSocketEnter", SocketName=sockeName, Movie=self.Game.Movie_Points, Filter=fil)
                tc.addTask("TaskFunction", Fn=und)
                with tc.addRepeatTask() as (tc_do, tc_until):
                    tc_do.addTask("AliasMultyplMovePlay", Movies=movv)
                    with tc_until.addRaceTask(2) as (tc_until_1, tc_until_2):
                        tc_until_1.addTask("TaskMovieSocketClick", SocketName=sockeName,
                                           Movie=self.Game.Movie_Points, isDown=True)
                        tc_until_1.addTask("TaskFunction", Fn=Click)

                        tc_until_2.addTask("TaskMovieSocketLeave", SocketName=sockeName, Movie=self.Game.Movie_Points)
                        pass
                    pass
                tc.addTask("TaskFunction", Fn=undLeav)
                tc.addTask("AliasMultyplMovePlay", Movies=movvRotate)
                tc.addTask("TaskFunction", Fn=RotateEnd)
                pass
            pass

        def EndAliase(self):
            dat = self.ManagerDatas[self.Value]
            if (dat.Disable is True):
                return
                pass
            id = int(self.Key)
            name = "RailRoadGame%d" % (id)
            if TaskManager.existTaskChain(name) is True:
                TaskManager.cancelTaskChain(name)
                pass
            pass

        def getTO(self):
            dat = self.ManagerDatas[self.Value]
            ManagerData = dat.ManagerData
            return [ManagerData.From, ManagerData.Id, ManagerData.To]
            pass

        def getData(self):
            dat = self.ManagerDatas[self.Value]
            return dat
            pass

        def ReHotspot(self):
            dat = self.ManagerDatas[self.Value]
            if (dat.Disable is True):
                return
                pass
            id = int(self.Key)
            sockeName = "socket_%d" % (id)
            hp = self.Game.Movie_Points.getEntity().getSocket(sockeName)
            hp.disable()
            hp.enable()
            pass

        pass

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(RailRoadGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.GameData = None
        self.InterDataSs = {}
        self.MovesMovies = {}

        self.Movie_Points = None
        self.Movie_L_R = None
        self.Movie_L_G = None
        self.Movie_B_On = None
        self.Movie_B_Off = None
        self.PlayMovie = False
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self.__PreInit()
        self.__InitIntersects()
        self.__DoAliases()
        pass

    def __PreInit(self):
        self.Movie_Points = self.object.getObject("Movie_Points")
        self.Movie_L_R = self.object.getObject("Movie_L_R")
        self.Movie_L_G = self.object.getObject("Movie_L_G")
        self.Movie_B_On = self.object.getObject("Movie_B_On")
        self.Movie_B_Off = self.object.getObject("Movie_B_Off")

        self.Movie_L_R.setEnable(False)
        self.Movie_L_G.setEnable(False)
        self.Movie_B_Off.setEnable(False)

        self.GameData = RailRoadGameManager.getGame(self.EnigmaName)
        for key, value in self.GameData.Intersect.iteritems():
            self.InterDataSs[key] = RailRoadGame.InterData(self, key)
            for int in value:
                self.InterDataSs[key].addData(int)
                pass
            pass

        for value in self.GameData.Movies:
            name = "%s_%s_%s" % (value.From, value.Midl, value.To)
            MovieName = value.Movie
            Movie = self.object.getObject(MovieName)
            if (Movie is None):
                Trace.log("Entity", 0, "cant find movie %s" % (MovieName))
                return
                pass
            Movie.setEnable(False)
            self.MovesMovies[name] = Movie
            pass

        pass

    def __InitIntersects(self):
        for key, value in self.GameData.Intersect.iteritems():
            dat = self.InterDataSs[key]
            dat.DoAliase()
            pass
        pass

    ###############################################

    def __DoAliases(self):
        self.__DoAliasButton()
        self.__DoAliasMove()
        pass

    def __DoAliasButton(self):
        name = "RailRoadGameClick"
        sockeName = "Click"
        movv = [[(self.Movie_B_Off, True)]]

        def und():
            self.Movie_B_Off.setEnable(True)
            pass

        def undLeav():
            self.Movie_B_Off.setEnable(False)
            pass

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketEnter", SocketName=sockeName, Movie=self.Movie_Points)
            tc.addTask("TaskFunction", Fn=und)
            with tc.addRepeatTask() as (tc_do, tc_until):
                tc_do.addTask("AliasMultyplMovePlay", Movies=movv)
                with tc_until.addRaceTask(2) as (tc_until_1, tc_until_2):
                    tc_until_1.addTask("TaskMovieSocketClick", SocketName=sockeName, Movie=self.Movie_Points, isDown=True)
                    tc_until_1.addTask("TaskNotify", ID=Notificator.onRailRoadGameMove)

                    tc_until_2.addTask("TaskMovieSocketLeave", SocketName=sockeName, Movie=self.Movie_Points)
                    tc_until_2.addTask("TaskFunction", Fn=undLeav)
                    pass
                pass
            pass
        pass

    def __DoAliasMove(self):
        name = "RailRoadGameMove"

        movv = [[(None, True)]]

        mov2 = [[(None, True)]]
        end = [False]

        def DoPath():
            self.PlayMovie = True
            mov = []
            datPrev = [0, 0, 0]
            while True:
                PrevFromId = datPrev[0]
                PrevCurId = datPrev[1]
                PrevToId = datPrev[2]
                if PrevToId not in self.InterDataSs:
                    Trace.log("Entity", 0, "%s PrevToId not in self.InterDataSs" % (PrevToId))
                    break
                    pass
                dat = self.InterDataSs[PrevToId]
                path = dat.getTO()
                FromId = path[0]
                CurId = path[1]
                ToId = path[2]
                name = "%s_%s_%s" % (FromId, CurId, ToId)
                if (FromId != PrevCurId):
                    if (ToId != PrevCurId):
                        break
                        pass
                    path[0] = ToId
                    path[2] = FromId
                    FromId = path[0]
                    CurId = path[1]
                    ToId = path[2]
                    pass
                name = "%s_%s_%s" % (FromId, CurId, ToId)
                if name not in self.MovesMovies:
                    Trace.log("Entity", 0, "%s name not in self.MovesMoviese" % (name))
                    break
                    pass

                movPlay = self.MovesMovies[name]
                movPlay.setEnable(True)
                time = movPlay.getDuration() * 999
                movPlay.getEntity().setTiming(time)
                mov.append((movPlay, True))
                datPrev = path
                pass
            last = self.InterDataSs[CurId]
            en = last.getData().ManagerData.Win
            end[0] = en
            movv[0] = mov
            pass

        def EndMove():
            if (end[0] is False):
                for mt in movv[0]:
                    mt[0].setEnable(False)
                    pass
                movv[0][0][0].setEnable(True)
                movv[0][0][0].getEntity().setTiming(0)
                self.Movie_L_R.setEnable(True)
                mov2[0] = [(self.Movie_L_R, True)]
                pass
            else:
                self.Movie_L_G.setEnable(True)
                mov2[0] = [(self.Movie_L_G, True)]
                pass

            pass

        def EndMove2():
            self.Movie_L_G.setEnable(False)
            self.Movie_L_R.setEnable(False)
            self.Movie_B_Off.setEnable(False)
            hp = self.Movie_Points.getEntity().getSocket("Click")
            hp.disable()
            hp.enable()
            if (end[0] is True):
                self.Movie_L_G.setEnable(True)
                self.__Win()
                pass

            for key, val in self.InterDataSs.iteritems():
                val.ReHotspot()
                pass

            self.PlayMovie = False
            pass

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskListener", ID=Notificator.onRailRoadGameMove)
            tc.addTask("TaskFunction", Fn=DoPath)
            tc.addTask("AliasMultyplMovePlay", Movies=movv)
            tc.addTask("TaskFunction", Fn=EndMove)
            tc.addTask("AliasMultyplMovePlay", Movies=mov2)
            tc.addTask("TaskFunction", Fn=EndMove2)
            pass
        pass

    def __Finita(self):
        name = "RailRoadGameMove"
        if TaskManager.existTaskChain(name) is True:
            TaskManager.cancelTaskChain(name)
            pass
        name = "RailRoadGameClick"
        if TaskManager.existTaskChain(name) is True:
            TaskManager.cancelTaskChain(name)
            pass

        for key, val in self.InterDataSs.iteritems():
            val.EndAliase()
            pass

        self.ReInitParamentrs()
        pass

    def __Win(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    pass
