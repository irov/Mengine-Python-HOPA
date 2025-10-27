from Foundation.TaskManager import TaskManager
from Notification import Notification

from ZumaTurret import ZumaTurret


# from HOPA.Enities.Zuma.ZumaTurret import ZumaTurret
Enigma = Mengine.importEntity("Enigma")


class Zuma(Enigma):
    ChainDelay = 0.2 * 1000  # speed fix

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        #        Type.addAction("Places")
        pass

    def __init__(self):
        super(Zuma, self).__init__()
        self.BallCount = 0
        self.Delta = 0.2
        self.BallCases = ["Sprite_Red", "Sprite_Blue", "Sprite_Yellow"]  # non-stohastic  patern
        self.Exit = Notification.addObserver(Notificator.onFinalize, self._stopEnigma)
        self.clean = []

        # Flow control
        self.flow = []
        self.active_flow = []
        self.timing = {}

        pass

    def _stopEnigma(self):
        self.__cleanUp()
        return True
        pass

    def _playEnigma(self):
        Gun = self.object.getObject("Sprite_Frogg")
        Tral = ZumaTurret(self.object, Gun)
        self.StartFlow()
        self.RunFlow()

    #        print self.flow

    def __genBallEssence(self):
        MovieObj = self.object.generateObject("MovieZuma%d" % (self.BallCount,), "Movie_Track")
        MovieObj.setSpeedFactor(0.7)
        self.__MovieJoinBall(MovieObj)
        self.BallCount += 1
        return MovieObj
        pass

    def __MovieJoinBall(self, MovieObj):
        color = self.BallCases[self.BallCount % 3]
        MovieEn = MovieObj.getEntity()
        slot = MovieEn.getMovieSlot("0")
        Ball = self.object.generateObject("BallZuma%d" % (self.BallCount,), color)
        BallEn = Ball.getEntity()
        slot.addChild(BallEn)
        self.clean.append(BallEn)
        pass

    def _complete(self, isSkip):
        pass

    def __cleanUp(self):
        if not self.clean:
            return
            pass
        for cl in self.clean:
            cl.removeFromParent()
            pass
        pass

    # Controll flow

    def StartFlow(self, flowLength=22):
        for balls in range(flowLength):
            Movie = self.__genBallEssence()
            self.flow.append(Movie)

        pass

    def RunFlow(self, From=None, To=None):
        flow = []
        if From is None and To is None:
            flow = self.flow
        else:
            flow = self.flow[From:To]
            pass
        self.active_flow = flow
        with TaskManager.createTaskChain(Name="RunFlow") as tc:
            for MovieBall in flow:
                tc.addDelay(Zuma.ChainDelay)
                tc.addTask("TaskMoviePlay", Movie=MovieBall, Wait=False, LastFrame=None)

        pass

    def StopBall(self, BallIndex):  # Stop behind index, 0 - stop all
        def Duration(isSkip):
            for i in self.flow:
                iEn = i.getEntity()
                self.timing[i] = iEn.getTiming()
            pass

        if len(self.flow) < BallIndex:
            return
        flow = self.active_flow[BallIndex:]
        self.active_flow = self.active_flow[BallIndex:]
        if not flow:
            return
        with TaskManager.createTaskChain(Name="StopBall", Cb=Duration) as tc:
            for MovieBall in flow:
                tc.addTask("TaskMovieStop", Movie=MovieBall)
                tc.addFunction(self.GetProgress, MovieBall)
        pass

    def SincronizeFlow(self):  #
        self.StopBall(0)
        #        val = self.timing.values()
        #        val.sort()

        pass

    def GetProgress(self, MovieObj):
        Movie = MovieObj  # self.flow[0] # first

    #        print "Progress :", self.timing

    def PushBall(self, BallIndex):
        pass

    def PopBall(self, BallIndex):
        pass
