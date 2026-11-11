from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager

class SystemManaFind(System):
    def __init__(self):
        super(SystemManaFind, self).__init__()
        self.onManaFindObserver = None
        self.findChainNames = []
        pass

    def _onRun(self):
        self.onManaFindObserver = Notification.addObserver(Notificator.onManaSearchBegin, self.__onManaSearchBegin)
        return True

    def _onStop(self):
        Notification.removeObserver(self.onManaFindObserver)
        self.onManaFindObserver = None

        for chain_name in self.findChainNames:
            TaskManager.cancelTaskChain(chain_name, exist=False)
        self.findChainNames = []
        pass

    def __onManaSearchBegin(self, movie, value):
        movie_name = movie.getName()
        tc_name = "FindMana_" + movie_name

        if TaskManager.existTaskChain(tc_name) is True:
            TaskManager.cancelTaskChain(tc_name)
            pass

        if tc_name not in self.findChainNames:
            self.findChainNames.append(tc_name)

        movieEntity = movie.getEntity()
        movedNode = movieEntity.getMovieSlot("slot")

        Mana = DemonManager.getDemon("Mana")
        ManaEntity = Mana.getEntity()
        pos = ManaEntity.getUpdatePosition()

        def __filter(check):
            if check is movie:
                return True
                pass
            return False
            pass

        time = 2.0
        time *= 1000  # speed fix

        with TaskManager.createTaskChain(Name=tc_name) as tc:
            with tc.addRepeatTask() as (tc_do, tc_until):
                tc_do.addTask("TaskMovieStop", Movie=movie)
                tc_do.addTask("TaskMovieLastFrame", Movie=movie, Value=False)
                tc_do.addTask("TaskMovieSocketEnter", Movie=movie, SocketName="socket")
                with tc_do.addRaceTask(2) as (tc_ok, tc_leave):
                    tc_ok.addTask("TaskMoviePlay", Movie=movie, Wait=True, Loop=False)
                    tc_ok.addNotify(Notificator.onManaFind, movie)

                    tc_leave.addTask("TaskMovieSocketLeave", Movie=movie, SocketName="socket")
                    pass

                tc_until.addListener(Notificator.onManaFind, Filter=__filter)
                pass
            with tc.addParallelTask(2) as (tc_1, tc_2):
                tc_1.addTask("TaskNodeBezier2To", Node=movedNode, To=pos, Time=time)

                tc_2.addTask("TaskNodeAlphaTo", Node=movieEntity, From=1.0, To=0.0, Time=time)
                pass
            tc.addDisable(movie)
            tc.addNotify(Notificator.onManaIncrease, value)
            pass
        return False
