from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager


class Charger(BaseEntity):
    States = ["Idle", "Enter", "Over", "Leave", "Release"]

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "ResourceMovieIdle")
        Type.addAction(Type, "ResourceMovieEnter")
        Type.addAction(Type, "ResourceMovieOver")
        Type.addAction(Type, "ResourceMovieLeave")
        Type.addAction(Type, "ResourceMovieRelease")
        Type.addAction(Type, "ResourceMovieCharge")
        Type.addAction(Type, "ResourceMovieCharged")

        Type.addAction(Type, "TimeReload", Update=Type.__updateTimeReload)
        Type.addAction(Type, "WaitCharge")
        Type.addAction(Type, "NoCharge")
        Type.addAction(Type, "State")
        pass

    def __updateTimeReload(self, value):
        if self.state == "Release":
            self.__updateChargeSpeedFactor()
            pass
        pass

    def __init__(self):
        super(Charger, self).__init__()

        self.tc = None
        self.state = "Idle"

        self.Movies = {}
        pass

    def _onInitialize(self, obj):
        super(Charger, self)._onInitialize(obj)

        def __createMovie(name, res, play, loop):
            if res is None:
                return None
                pass

            if Mengine.hasResource(res) is False:
                return False
                pass

            resource = Mengine.getResourceReference(res)

            if resource is None:
                Trace.log("Entity", 0, "Charger._onInitialize: not fount resource %s" % (res))
                return None
                pass

            mov = ObjectManager.createObjectUnique("Movie", name, self.object, ResourceMovie=resource)
            mov.setEnable(False)
            mov.setPlay(play)
            mov.setLoop(loop)

            movEntity = mov.getEntityNode()
            self.addChild(movEntity)

            self.Movies[name] = mov

            return mov
            pass

        if __createMovie("Idle", self.ResourceMovieIdle, True, True) is False:
            self.initializeFailed("Charger not have Idle resource '%s'" % (self.ResourceMovieIdle))
            return False
            pass

        if __createMovie("Charge", self.ResourceMovieCharge, False, False) is False:
            return False
            pass

        __createMovie("Enter", self.ResourceMovieEnter, False, False)
        __createMovie("Over", self.ResourceMovieOver, True, True)
        __createMovie("Leave", self.ResourceMovieLeave, False, False)
        __createMovie("Release", self.ResourceMovieRelease, False, False)
        __createMovie("Charged", self.ResourceMovieCharged, False, False)

        return True
        pass

    def __updateChargeSpeedFactor(self):
        MovieCharge = self.Movies.get("Charge")
        MovieChargeEntity = MovieCharge.getEntity()
        charge_duration = MovieChargeEntity.getDuration()
        charge_speedfactor = charge_duration / float(self.TimeReload)
        MovieCharge.setSpeedFactor(charge_speedfactor)
        pass

    def __setState(self, state, debug):
        self.state = state
        pass

    def __stateIdle(self, source, MovieIdle):
        source.addEnable(MovieIdle)

        with source.addRaceTask(2) as (source_idle_enter, source_idle_listener):
            source_idle_enter.addTask("TaskMovieSocketEnter", SocketName="socket", Movie=MovieIdle)
            source_idle_enter.addFunction(self.__setState, "Enter", 11)

            source_idle_listener.addListener(Notificator.onChargerRun,
                                         Filter=lambda obj: obj is self.object)
            source_idle_listener.addFunction(self.__setState, "Release", 12)
            pass

        source.addDisable(MovieIdle)
        pass

    def __stateEnter(self, source, MovieEnter):
        if MovieEnter is None:
            source.addFunction(self.__setState, "Over", 25)

            return
            pass

        source.addEnable(MovieEnter)

        with source.addRaceTask(4) as (
        source_enter_movie, source_enter_click, source_enter_leave, source_enter_listener):
            source_enter_movie.addTask("TaskMoviePlay", Movie=MovieEnter)
            source_enter_movie.addFunction(self.__setState, "Over", 21)

            source_enter_click.addTask("TaskMovieSocketClick", SocketName="socket", Movie=MovieEnter, isDown=True)
            source_enter_click.addFunction(self.__setState, "Release", 22)

            source_enter_leave.addTask("TaskMovieSocketLeave", SocketName="socket", Movie=MovieEnter)
            source_enter_leave.addFunction(self.__setState, "Idle", 23)

            source_enter_listener.addListener(Notificator.onChargerRun, Filter=lambda obj: obj is self.object)
            source_enter_listener.addFunction(self.__setState, "Release", 24)
            pass

        source.addDisable(MovieEnter)
        pass

    def __stateOver(self, source, MovieOver):
        source.addEnable(MovieOver)

        with source.addRaceTask(3) as (source_over_click, source_over_leave, source_over_listener):
            source_over_click.addTask("TaskMovieSocketClick", SocketName="socket", Movie=MovieOver, isDown=True)
            source_over_click.addFunction(self.__setState, "Release", 31)

            source_over_leave.addTask("TaskMovieSocketLeave", SocketName="socket", Movie=MovieOver)
            source_over_leave.addFunction(self.__setState, "Leave", 32)

            source_over_listener.addListener(Notificator.onChargerRun, Filter=lambda obj: obj is self.object)
            source_over_listener.addFunction(self.__setState, "Release", 33)
            pass

        source.addDisable(MovieOver)
        pass

    def __stateLeave(self, source, MovieLeave):
        if MovieLeave is None:
            source.addFunction(self.__setState, "Idle", 44)

            return
            pass

        source.addEnable(MovieLeave)

        with source.addRaceTask(3) as (source_leave_movie, source_leave_enter, source_leave_listener):
            source_leave_movie.addTask("TaskMoviePlay", Movie=MovieLeave)
            source_leave_movie.addFunction(self.__setState, "Idle", 41)

            source_leave_enter.addTask("TaskMovieSocketEnter", SocketName="socket", Movie=MovieLeave)
            source_leave_enter.addFunction(self.__setState, "Over", 42)

            source_leave_listener.addListener(Notificator.onChargerRun, Filter=lambda obj: obj is self.object)
            source_leave_listener.addFunction(self.__setState, "Release", 43)
            pass

        source.addDisable(MovieLeave)
        pass

    def __stateCharge(self, source, MovieRelease, MovieCharge, MovieCharged):
        if MovieRelease is not None:
            with source.addParallelTask(2) as (source_release_movie, source_release_listener):
                source_release_movie.addEnable(MovieRelease)
                with source_release_movie.addRaceTask(2) as (source_release_movie_1, source_release_movie_2):
                    source_release_movie_1.addTask("TaskMoviePlay", Movie=MovieRelease)
                    source_release_movie_1.addDisable(MovieRelease)
                    source_release_movie_1.addEnable(MovieCharge)

                    source_release_movie_2.addListener(Notificator.onChargerSkip, Filter=lambda obj: obj is self.object)
                    source_release_movie_2.addFunction(self.object.setState, "Skip")
                    source_release_movie_2.addBlock()
                    pass

                if self.WaitCharge is True:
                    source_release_listener.addTaskaddListener(Notificator.onChargerCharge, Filter=lambda obj: obj is self.object)
                    pass
                pass
            pass
        else:
            source.addEnable(MovieCharge)
            if self.WaitCharge is True:
                source.addListener(Notificator.onChargerCharge, Filter=lambda obj: obj is self.object)
                pass
            pass

        if self.NoCharge is False:
            with source.addIfTask(lambda obj: obj.getState() != "Skip", self.object) as (source_true, source_else):
                with source_true.addRaceTask(2) as (source_charge_1, source_charge_2):
                    source_charge_1.addFunction(self.__updateChargeSpeedFactor)
                    source_charge_1.addTask("TaskMoviePlay", Movie=MovieCharge)

                    source_charge_2.addListener(Notificator.onChargerSkip, Filter=lambda obj: obj is self.object)
                    pass
                pass
            pass

        source.addDisable(MovieCharge)

        if MovieCharged is not None:
            source.addEnable(MovieCharged)
            source.addTask("TaskMoviePlay", Movie=MovieCharged)
            source.addDisable(MovieCharged)
            pass
        pass

    def __stateReturn(self, source, MovieOver):
        source.addEnable(MovieOver)

        with source.addRaceTask(2) as (source_release_enter, source_release_leave):
            source_release_enter.addTask("TaskMovieSocketEnter", SocketName="socket", Movie=MovieOver)
            source_release_enter.addFunction(self.__setState, "Over", 11)

            source_release_leave.addTask("TaskMovieSocketLeave", SocketName="socket", Movie=MovieOver)
            source_release_leave.addFunction(self.__setState, "Idle", 12)
            pass

        source.addDisable(MovieOver)
        pass

    def _onActivate(self):
        super(Charger, self)._onActivate()

        self.tc = TaskManager.createTaskChain(Repeat=True)

        MovieIdle = self.Movies.get("Idle")
        MovieEnter = self.Movies.get("Enter")
        MovieOver = self.Movies.get("Over", MovieIdle)
        MovieLeave = self.Movies.get("Leave")
        MovieRelease = self.Movies.get("Release")
        MovieCharge = self.Movies.get("Charge")
        MovieCharged = self.Movies.get("Charged")

        with self.tc as tc_repeat:
            def __states(isSkip, cb):
                index = Charger.States.index(self.state)

                cb(isSkip, index)
                pass

            with tc_repeat.addSwitchTask(5, __states) as (source_idle, source_enter, source_over, source_leave, source_release):
                source_idle.addFunction(self.object.setState, "Idle")
                source_idle.addScope(self.__stateIdle, MovieIdle)
                source_enter.addScope(self.__stateEnter, MovieEnter)
                source_over.addScope(self.__stateOver, MovieOver)
                source_leave.addScope(self.__stateLeave, MovieLeave)

                source_release.addFunction(self.object.setState, "Charge")
                source_release.addNotify(Notificator.onChargerRelease, self.object)
                source_release.addScope(self.__stateCharge, MovieRelease, MovieCharge, MovieCharged)
                source_release.addScope(self.__stateReturn, MovieOver)
                source_release.addNotify(Notificator.onChargerReload, self.object)

    def _onDeactivate(self):
        super(Charger, self)._onDeactivate()

        self.tc.cancel()

        for mov in self.Movies.itervalues():
            mov.setEnable(False)

    def _onFinalize(self):
        super(Charger, self)._onFinalize()

        for mov in self.Movies.itervalues():
            mov.onDestroy()

        self.Movies = {}
