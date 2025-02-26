from Foundation.TaskManager import TaskManager
from HOPA.ShootGameManager import ShootGameManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class ShootGame(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(ShootGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Game = None
        self.ShootCountStart = 0
        self.ShootWin = 0

        self.ShootCountCurrent = 0
        self.ShootCountDo = 0
        self.MoviePoints = None

        self.ShootMovie = []
        self.ShootWinMovie = []
        self.MoviesDug = []
        self.MoviesTime = []
        self.PathLen = []

        self.AliasNames = []
        self.Start = False
        self.CurentPlayMovie = None
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
        self.Game = ShootGameManager.getGame(self.EnigmaName)
        self.ShootCountStart = self.Game.ShootCount
        self.ShootCountCurrent = self.ShootCountStart
        self.ShootWin = self.Game.ShootWin

        self.ShootMovie = self.object.getObject("Movie_Shoots")
        self.ShootWinMovie = self.object.getObject("Movie_Shoots_Win")
        self.MoviePoints = self.object.getObject("Movie_Points")

        for path in self.Game.Pathes:
            MovieName = path.Movie
            tic = path.TimeShotDec
            movie = self.object.getObject(MovieName)
            PathLen = path.PathLen
            self.MoviesDug.append(movie)
            self.MoviesTime.append(tic)
            self.PathLen.append(PathLen)
            pass
        pass

    def __Init(self):
        name = "ShootGame Start"

        def fun():
            if (self.Start is True):
                return
                pass

            self.Start = True
            self.__StartGame()

            pass

        with TaskManager.createTaskChain(Name=name, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName="Start", Movie=self.MoviePoints, isDown=True)
            tc.addTask("TaskFunction", Fn=fun)
            pass
        pass

    def __StartGame(self):
        self._UpdateScore_In()
        self._DoAliase()
        pass

    def __EndGame(self):
        self._EndAliase()

        self.ReInit()
        self.Start = False

        pass

    def ReInit(self):
        self.ShootCountCurrent = self.ShootCountStart
        self.ShootCountDo = 0
        for movI in self.MoviesDug:
            movI.setEnable(False)
            pass
        pass

    def _DoAliase(self):
        self.setEventListener(onGlobalHandleMouseButtonEventEnd=self._onGlobalHandleMouseButtonEventEnd)
        self.enableGlobalMouseEvent(True)

        for id in range(len(self.MoviesDug)):
            self._DoAliase_In(id)
            pass

        AliasName = "ShootGameMovie"
        self.AliasNames.append(AliasName)
        moviePlay = [[(None, True)]]

        preRand = [-1]

        def PrePlay():
            for movI in self.MoviesDug:
                movI.setEnable(False)
                pass

            rand = Mengine.rand(len(self.MoviesDug))
            while rand == preRand[0]:
                rand = Mengine.rand(len(self.MoviesDug))
                pass
            preRand[0] = rand

            mov = self.MoviesDug[rand]
            mov.setEnable(True)
            moviePlay[0] = [(mov, True)]
            lenPath = self.PathLen[rand]
            tim = self.MoviesTime[rand]
            tim *= self.ShootCountDo
            mov_Time = mov.getDuration()
            mov_Time1 = mov_Time / lenPath
            speed = mov_Time1 / (mov_Time1 - tim)

            mov.setSpeedFactor(speed)
            self.CurentPlayMovie = mov
            pass

        with TaskManager.createTaskChain(Name=AliasName, Repeat=True) as tc:
            tc.addTask("TaskFunction", Fn=PrePlay)
            tc.addTask("AliasMultyplMovePlay", Movies=moviePlay)
            pass
        pass

    def _EndAliase(self):
        self.setEventListener(onGlobalHandleMouseButtonEventEnd=None)
        self.enableGlobalMouseEvent(False)
        for alName in self.AliasNames:
            self.__canTT(alName)
            pass
        self.AliasNames = []
        pass

    def _onGlobalHandleMouseButtonEventEnd(self, touchId, button, isDown):
        if button != 0 or isDown is False:
            return
            pass

        self.ShootCountCurrent = self.ShootCountCurrent - 1
        self._UpdateScore_In()

        self.TryEnd()
        pass

    def TryEnd(self):
        if (self.ShootWin == self.ShootCountDo):
            self.__EndGame()
            self.__Finita()
            self.enigmaComplete()
            pass

        elif (self.ShootCountCurrent == 0):
            Notification.notify(Notificator.onShootGameRestart)
            self.__EndGame()
            pass

        pass

    def _DoAliase_In(self, id):
        movie = self.MoviesDug[id]

        def shoot():
            if (self.CurentPlayMovie is None):
                return
                pass

            self.ShootCountDo = self.ShootCountDo + 1
            tim = self.CurentPlayMovie.getDuration() - 1
            self.CurentPlayMovie.getEntity().setTiming(tim)
            pass

        for i in range(self.PathLen[id]):
            AliasName = "ShootGame_Click_%d_%d" % (id, i)
            socketName = "P%d_%d" % (id + 1, i + 1)
            with TaskManager.createTaskChain(Name=AliasName, Repeat=True) as tc:
                tc.addTask("TaskMovieSocketClick", SocketName=socketName, Movie=movie, isDown=True)
                tc.addTask("TaskFunction", Fn=shoot)
                pass
            pass
            self.AliasNames.append(AliasName)
        pass

    def _UpdateScore_In(self):
        tim1 = self.ShootMovie.getDuration()
        tim2 = self.ShootWinMovie.getDuration()
        tim1_tic = tim1 / self.ShootCountStart
        tim2_tic = tim2 / self.ShootWin
        setTime1 = tim1_tic * self.ShootCountCurrent
        setTime2 = tim2_tic * self.ShootCountDo
        if (setTime1 == tim1):
            setTime1 = setTime1 - 1
            pass

        if (setTime2 == tim2):
            setTime2 = setTime2 - 1
            pass

        self.ShootMovie.getEntity().setTiming(setTime1)
        self.ShootWinMovie.getEntity().setTiming(setTime2)
        pass

    def __Finita(self):
        self.__canTT("ShootGame Start")
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass
