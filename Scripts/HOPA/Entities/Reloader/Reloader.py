from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager


class Reloader(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("ResourceMovieIdle")
        Type.addAction("ResourceMovieBegin")
        Type.addAction("ResourceMovieProcess")
        Type.addAction("ResourceMovieEnd")

        Type.addAction("Time", Update=Type.__updateTime)
        pass

    def __init__(self):
        super(Reloader, self).__init__()

        self.Movies = {}
        pass

    def __updateTime(self, value):
        Movie_Process = self.Movies.get("Process")
        Movie_ProcessEntity = Movie_Process.getEntity()
        charge_duration = Movie_ProcessEntity.getDuration()
        charge_speedfactor = charge_duration / float(value)

        Movie_Process.setSpeedFactor(charge_speedfactor)
        pass

    def _onInitialize(self, obj):
        super(Reloader, self)._onInitialize(obj)

        def __createMovie(Name, Resource, Play=False, Loop=False):
            if Resource is None:
                return False
                pass

            mov = ObjectManager.createObjectUnique("Movie", Name, self.object, ResourceMovie=Resource)
            mov.setEnable(False)
            mov.setPlay(Play)
            mov.setLoop(Loop)

            movEntity = mov.getEntityNode()
            self.addChild(movEntity)

            self.Movies[Name] = mov

            return True
            pass

        if __createMovie("Process", self.ResourceMovieProcess) is False:
            return False
            pass

        __createMovie("Idle", self.ResourceMovieIdle, True, True)
        __createMovie("Begin", self.ResourceMovieBegin)
        __createMovie("End", self.ResourceMovieEnd)

        return True
        pass

    def _onActivate(self):
        super(Reloader, self)._onActivate()

        self.tc = TaskManager.createTaskChain(Repeat=True)

        MovieIdle = self.Movies.get("Idle")
        MovieBegin = self.Movies.get("Begin")
        MovieProcess = self.Movies.get("Process")
        MovieEnd = self.Movies.get("End")

        with self.tc as source:
            if MovieIdle is not None:
                source.addEnable(MovieIdle)
                source.addListener(Notificator.onReloaderBegin, Filter=lambda obj: obj is self.object)
                source.addDisable(MovieIdle)
                pass

            source.addTask("TaskMoviePlay", Movie=MovieBegin, AutoEnable=True)
            ###
            with source.addRepeatTask() as (source_do, source_until):
                source_do.addListener(Notificator.onZombieTimePause)
                source_do.addParam(MovieProcess, "Pause", True)
                source_do.addListener(Notificator.onZombieTimeResume)
                source_do.addParam(MovieProcess, "Pause", False)

                source_until.addTask("TaskMoviePlay", Movie=MovieProcess, AutoEnable=True)
                pass
            ###
            # source.addTask("TaskMoviePlay", Movie = MovieProcess, AutoEnable = True)
            source.addTask("TaskMoviePlay", Movie=MovieEnd, AutoEnable=True)

            source.addNotify(Notificator.onReloaderEnd, self.object)
            pass
        pass

    def _onDeactivate(self):
        super(Reloader, self)._onDeactivate()

        self.tc.cancel()
        self.tc = None

        for mov in self.Movies.itervalues():
            mov.setEnable(False)
            pass
        pass

    def _onFinalize(self):
        super(Reloader, self)._onFinalize()

        for mov in self.Movies.itervalues():
            mov.onDestroy()
            pass

        self.Movies = {}
