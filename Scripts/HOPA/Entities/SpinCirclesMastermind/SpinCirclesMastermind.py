from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

from SpinCirclesMastermindManager import SpinCirclesMastermindManager

Enigma = Mengine.importEntity("Enigma")

class SpinCirclesMastermind(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addActionActivate(Type, "UpNum")
        Type.addActionActivate(Type, "DownNum")
        pass

    def __init__(self):
        super(SpinCirclesMastermind, self).__init__()
        self.SpinCircles = None
        self.upNumCollection = {}
        self.downNumCollection = {}
        self.MovieTrigger = None
        self.WinParam = 0
        pass

    def _onPreparation(self):
        super(SpinCirclesMastermind, self)._onPreparation()
        mastermindData = SpinCirclesMastermindManager.getSpinCirclesMastermind(self.EnigmaName)
        spinName = mastermindData.getSpinName()

        bulls = mastermindData.getBulls()

        for num, objName in bulls.iteritems():
            movie = self.object.getObject(objName)
            movie.setEnable(False)
            self.upNumCollection[num] = movie
            pass

        cows = mastermindData.getCows()

        for num, objName in cows.iteritems():
            movie = self.object.getObject(objName)
            movie.setEnable(False)
            self.downNumCollection[num] = movie
            pass

        movieTriggerName = mastermindData.getTriggerName()
        self.MovieTrigger = self.object.getObject(movieTriggerName)

        self.WinParam = mastermindData.getSize()
        self.SpinCircles = EnigmaManager.getEnigmaObject(spinName)

        MovieTriggerEntity = self.MovieTrigger.getEntity()
        self.TriggerSocket = MovieTriggerEntity.getSocket("Enter")
        pass

    def _onActivate(self):
        super(SpinCirclesMastermind, self)._onActivate()
        pass

    def __playTasks(self):
        if TaskManager.existTaskChain(self.EnigmaName) is True:
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        with TaskManager.createTaskChain(Name=self.EnigmaName) as tc:
            tc.addTask("TaskSetParam", Object=self.SpinCircles, Param="Play", Value=True)
            tc.addTask("TaskFunction", Fn=self.dataPreparation)
            with tc.addRepeatTask() as (tc_do, tc_until):
                with tc_do.addRaceTask(2) as (tc_click, tc_wait):
                    tc_click.addTask("TaskMovieSocketClick", Movie=self.MovieTrigger, SocketName="Enter")
                    tc_click.addTask("TaskFunction", Fn=self.blockInput, Args=(True,))
                    tc_click.addTask("TaskFunction", Fn=self.dataPreparation)
                    tc_click.addTask("TaskMoviePlay", Movie=self.MovieTrigger, Wait=False)
                    tc_click.addTask("TaskScope", Scope=self.playNumMovies)

                    tc_wait.addTask("TaskListener", ID=Notificator.onSpin)
                    tc_wait.addTask("TaskFunction", Fn=self.TriggerSocket.disable)
                    tc_wait.addTask("TaskListener", ID=Notificator.onSpinMove)
                    tc_wait.addTask("TaskFunction", Fn=self.TriggerSocket.enable)
                    pass
                tc_until.addTask("TaskListener", ID=Notificator.onSpinWin)
            pass

    def blockInput(self, value):
        spinEn = self.SpinCircles.getEntity()
        spinEn.blockSockets(value)
        pass

    def playNumMovies(self, scope):
        bullKey = self.object.getUpNum()
        cowsKey = self.object.getDownNum()

        upMovie = self.upNumCollection[bullKey]
        downMovie = self.downNumCollection[cowsKey]

        with scope.addParallelTask(2) as (tc_bulls, tc_cows):
            tc_bulls.addTask("TaskEnable", Object=upMovie)
            tc_bulls.addTask("TaskMoviePlay", Movie=upMovie)
            tc_bulls.addTask("TaskEnable", Object=upMovie, Value=False)

            tc_cows.addTask("TaskEnable", Object=downMovie)
            tc_cows.addTask("TaskMoviePlay", Movie=downMovie)
            tc_cows.addTask("TaskEnable", Object=downMovie, Value=False)
        scope.addTask("TaskFunction", Fn=self.isWin)
        scope.addTask("TaskFunction", Fn=self.blockInput, Args=(False,))
        pass

    def isWin(self):
        if self.object.getUpNum() == self.object.getDownNum() == self.WinParam:
            Notification.notify(Notificator.onSpinWin)
            self.setComplete()
            return True
            pass
        return False
        pass

    def _resetEnigma(self):
        self.dataPreparation()
        pass

    def dataPreparation(self):
        spinEn = self.SpinCircles.getEntity()
        TwistCollection = spinEn.getTwistCollection()
        tmpBulls = 0
        tmpCows = 0
        finals = []
        current = []
        for key, item in TwistCollection.iteritems():
            finals.append(item.getFinalState())
            current.append(item.getState())
            pass

        current = list(set(current))
        for value in current:
            if value in finals:
                tmpBulls += 1
                pass
            pass

        for key, item in TwistCollection.iteritems():
            if item.getFinalState() == item.getState():
                tmpCows += 1
                pass
            pass

        self.object.setParam("UpNum", tmpBulls)
        self.object.setParam("DownNum", tmpCows)
        pass

    def _playEnigma(self):
        self.__playTasks()

        pass

    def _onDeactivate(self):
        super(SpinCirclesMastermind, self)._onDeactivate()

        pass

    def _stopEnigma(self):
        super(SpinCirclesMastermind, self)._stopEnigma()
        if TaskManager.existTaskChain(self.EnigmaName) is True:
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        self.SpinCircles = None
        self.upNumCollection = {}
        self.downNumCollection = {}
        self.MovieTrigger = None
        self.WinParam = 0
        pass

    pass