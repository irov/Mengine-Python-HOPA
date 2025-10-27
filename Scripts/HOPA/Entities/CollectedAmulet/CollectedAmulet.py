from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from CollectedAmuletManager import CollectedAmuletManager


class CollectedAmulet(BaseEntity):
    LOCKED = "Locked"
    READY = "Ready"
    IDLE = "Idle"
    USE = "Use"
    FAIL = "Fail"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("CurrentState", Update=CollectedAmulet.__updateCurrentState)
        Type.addActionActivate("CurrentCount", Update=CollectedAmulet.__updateCurrentCount)
        Type.addAction("Size")
        Type.addAction("HintPoint")
        pass

    def __init__(self):
        super(CollectedAmulet, self).__init__()
        self.isValidUse = False
        pass

    def __updateCurrentState(self, value):
        if value == CollectedAmulet.LOCKED:
            self.__lockedChain()
            pass

        if value == CollectedAmulet.READY:
            self.__readyChain()
            pass

        if value == CollectedAmulet.IDLE:
            self.__idleChain()
            pass

        if value == CollectedAmulet.FAIL:
            self.__failChain()
            pass

        if value == CollectedAmulet.USE:
            self.__useChain()
            pass
        pass

    def __lockedChain(self):
        self.cancelStateTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)
        movie = Data.getState(self.CurrentState)
        with TaskManager.createTaskChain(Name="Locked_" + self.object.getName()) as tc_locked:
            tc_locked.addEnable(movie)
            tc_locked.addTask("TaskMoviePlay", Movie=movie, Wait=False, Loop=True)
            pass
        pass

    def __useChain(self):
        self.cancelStateTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)
        movie = Data.getState(self.CurrentState)
        with TaskManager.createTaskChain(Name="Use_" + self.object.getName()) as tc_use:
            tc_use.addEnable(movie)
            tc_use.addTask("TaskMoviePlay", Movie=movie, Wait=True, Loop=False)
            tc_use.addNotify(Notificator.onCollectedAmuletUse)
            tc_use.addFunction(self.setValid, False)
            tc_use.addParam(self.object, "CurrentState", CollectedAmulet.LOCKED)
            tc_use.addParam(self.object, "CurrentCount", 0)
            pass
        pass

    def __readyChain(self):
        self.cancelStateTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)
        self.__disableValuesMovies(Data)
        movie = Data.getState(self.CurrentState)
        with TaskManager.createTaskChain(Name="Ready_" + self.object.getName()) as tc_ready:
            tc_ready.addTask("TaskEnable", Object=movie)
            tc_ready.addTask("TaskMoviePlay", Movie=movie, Wait=True, Loop=False)
            tc_ready.addParam(self.object, "CurrentState", CollectedAmulet.IDLE)
            pass
        pass

    def __failChain(self):
        self.cancelStateTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)
        movie = Data.getState(self.CurrentState)

        with TaskManager.createTaskChain(Name="Fail_" + self.object.getName()) as tc_fail:
            with tc_fail.addParallelTask(2) as (tc_1, tc_2):
                tc_1.addEnable(movie)
                tc_1.addTask("TaskMoviePlay", Movie=movie, Wait=True, Loop=False)

                tc_2.addTask("AliasMindPlay", MindID="ID_MIND_INVALID_AMULET")
                pass
            tc_fail.addParam(self.object, "CurrentState", CollectedAmulet.IDLE)
            pass
        pass

    def __idleChain(self):
        self.cancelStateTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)

        movie = Data.getState(self.CurrentState)
        with TaskManager.createTaskChain(Name="Idle_" + self.object.getName()) as tc_locked:
            tc_locked.addEnable(movie)
            tc_locked.addTask("TaskMoviePlay", Movie=movie, Wait=False, Loop=True)
            pass

        socket = Data.getSocket()
        with TaskManager.createTaskChain(Name="Click_" + self.object.getName()) as tc_click:
            tc_click.addTask("TaskSocketClick", Socket=socket)
            tc_click.addTask("TaskMouseButtonClickEnd", isDown=True)
            with tc_click.addSwitchTask(2, self.__isValidUse) as (tc_ok, tc_no):
                tc_ok.addParam(self.object, "CurrentState", CollectedAmulet.USE)

                tc_no.addParam(self.object, "CurrentState", CollectedAmulet.FAIL)
                pass
            pass
        pass

    def __isValidUse(self, isSkip, cb):
        if self.isValidUse is False:
            cb(isSkip, 1)
            return
            pass
        else:
            cb(isSkip, 0)
            return
            pass
        pass

    def setValid(self, value):
        self.isValidUse = value
        pass

    def __updateCurrentCount(self, value):
        if self.CurrentState != CollectedAmulet.LOCKED:
            return
            pass
        self.__valueChain(value)
        pass

    def __valueChain(self, value):
        self.cancelValueTaskChains()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableValuesMovies(Data)
        movie = Data.getValue(value)
        wait = False
        loop = True
        if value == self.Size:
            wait = True
            loop = False
            pass
        with TaskManager.createTaskChain(Name="Count_" + self.object.getName()) as tc_count:
            tc_count.addEnable(movie)
            tc_count.addTask("TaskMoviePlay", Movie=movie, Wait=wait, Loop=loop)
            if value == self.Size:
                tc_count.addParam(self.object, "CurrentState", CollectedAmulet.READY)
                pass
            pass
        pass

    def __disableStatesMovies(self, Data):
        states = Data.getStates()
        for movie in states.values():
            movie.setEnable(False)
            pass
        pass

    def __disableValuesMovies(self, Data):
        values = Data.getValues()
        for movie in values.values():
            movie.setEnable(False)
            pass
        pass

    def _onPreparation(self):
        super(CollectedAmulet, self)._onPreparation()
        Data = CollectedAmuletManager.getData(self.object)
        self.__disableStatesMovies(Data)
        self.__disableValuesMovies(Data)
        pass

    def _onActivate(self):
        super(CollectedAmulet, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(CollectedAmulet, self)._onDeactivate()
        self.cancelStateTaskChains()
        self.cancelValueTaskChains()
        pass

    def cancelStateTaskChains(self):
        if TaskManager.existTaskChain("Locked_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Locked_" + self.object.getName())
            pass

        if TaskManager.existTaskChain("Ready_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Ready_" + self.object.getName())
            pass

        if TaskManager.existTaskChain("Idle_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Idle_" + self.object.getName())
            pass

        if TaskManager.existTaskChain("Click_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Click_" + self.object.getName())
            pass

        if TaskManager.existTaskChain("Fail_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Fail_" + self.object.getName())
            pass
        pass

    def cancelValueTaskChains(self):
        if TaskManager.existTaskChain("Count_" + self.object.getName()):
            TaskManager.cancelTaskChain("Count_" + self.object.getName())
            pass
        pass

    pass
