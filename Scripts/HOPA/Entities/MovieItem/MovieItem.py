from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager


class MovieItem(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("ResourceMovieIdle")
        Type.addAction("ResourceMoviePick")
        pass

    def __init__(self):
        super(MovieItem, self).__init__()
        self.tc = None
        self.state = "Idle"

        self.Movies = {}

        self.SemaphoreInteractive = Semaphore(False, "Interactive")
        pass

    def getCurrentMovie(self):
        if self.state not in self.Movies:
            return None
            pass

        Movie = self.Movies.get(self.state)

        if Movie is None:
            return None
            pass

        return Movie
        pass

    def getHintPoint(self):
        Point = None

        CurrentMovie = self.getCurrentMovie()

        if CurrentMovie is None:
            CurrentMovie = self.Movies.get("Idle")
            pass

        if CurrentMovie is None:
            Trace.log("Entity", 0, "MovieItem.getHintPoint: not found current movie '%s' movies '%s'" % (self.state, self.Movies))

            return Mengine.vec2f(0.0, 0.0)
            pass

        if CurrentMovie.hasSlot('hint') is True:
            slot = CurrentMovie.getMovieSlot('hint')

            Point = slot.getWorldPosition()
        else:
            MovieSocket = CurrentMovie.getSocket('socket')

            Point = MovieSocket.getWorldPolygonCenter()
            pass

        if Point is None:
            return Mengine.vec2f(0.0, 0.0)
            pass

        return Point
        pass

    def _onInitialize(self, obj):
        super(MovieItem, self)._onInitialize(obj)

        def __createMovie(name, res, play, loop):
            if res is None:
                return None
                pass

            if Mengine.hasResource(res) is False:
                return False
                pass

            resource = Mengine.getResourceReference(res)

            if resource is None:
                Trace.log("Entity", 0, "MovieItem._onInitialize: not found resource %s" % (res))
                return None
                pass

            mov = ObjectManager.createObjectUnique("Movie", name, self.object, ResourceMovie=resource)
            mov.setEnable(False)
            mov.setPlay(play)
            mov.setLoop(loop)

            movEntityNode = mov.getEntityNode()
            self.addChild(movEntityNode)

            self.Movies[name] = mov

            return mov
            pass

        __createMovie("Idle", self.ResourceMovieIdle, True, True)
        __createMovie("Pick", self.ResourceMoviePick, False, False)

        return True
        pass

    def getPickEffectResourceName(self):
        if "Pick" in self.Movies:
            return self.ResourceMoviePick

        if "Idle" in self.Movies:
            return self.ResourceMovieIdle

        return None

    def _updateInteractive(self, value):
        self.SemaphoreInteractive.setValue(value)

    def __setState(self, state):
        # print " [MovieItem] state", self.getName(), state
        self.state = state
        pass

    def smartEnableMovie(self, MovieToEnable):
        if MovieToEnable.getEnable() is True:
            return

        for Movie in self.Movies.itervalues():
            if Movie is not MovieToEnable:
                Movie.setEnable(False)

        MovieToEnable.setEnable(True)

    def __stateIdle(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)

        with source.addRaceTask(2) as (source_click, source_enter):
            source_click.addTask("TaskMovieSocketClick", SocketName="socket", Movie=MovieIdle, isDown=True)

            source_click.addFunction(self.__setState, "Pick")

            source_enter.addTask("TaskMovieSocketEnter", SocketName="socket", Movie=MovieIdle)
            source_enter.addFunction(self.__setState, "Enter")
        pass

    def __stateEnter(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)

        source.addNotify(Notificator.onMovieItemEnter, self.object)

        with source.addRaceTask(2) as (source_click, source_leave):
            source_click.addTask("TaskMovieSocketClick", SocketName="socket", Movie=MovieIdle, isDown=True)
            source_click.addNotify(Notificator.onMovieItemLeave, self.object)

            source_click.addFunction(self.__setState, "Pick")

            source_leave.addTask("TaskMovieSocketLeave", SocketName="socket", Movie=MovieIdle)
            source_leave.addFunction(self.__setState, "Leave")

    def __stateLeave(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)

        source.addNotify(Notificator.onMovieItemLeave, self.object)
        source.addFunction(self.__setState, "Idle")

    def __statePick(self, source, MoviePick):
        if MoviePick is None:
            source.addNotify(Notificator.onMovieItemClick, self.object)
            source.addNotify(Notificator.onMovieItemPick, self.object)
            source.addFunction(self.__setState, "Idle")
            return
            pass

        source.addFunction(self.smartEnableMovie, MoviePick)

        source.addNotify(Notificator.onMovieItemClick, self.object)
        source.addTask("TaskMoviePlay", Movie=MoviePick)
        source.addNotify(Notificator.onMovieItemPick, self.object)
        source.addFunction(self.__setState, "Idle")
        pass

    def __stateInteractive(self, source, MovieIdle):
        socket = MovieIdle.getSocket('socket')

        source.addFunction(self.smartEnableMovie, MovieIdle)
        source.addFunction(socket.enable)

        source.addFunction(self.__setState, "Idle")

    def __stateUnInteractive(self, source, MovieIdle):
        socket = MovieIdle.getSocket('socket')

        source.addFunction(self.smartEnableMovie, MovieIdle)
        source.addFunction(socket.disable)

        source.addBlock()

    def checkInteractive(self):
        return self.object.getParam("Interactive") > 0

    def _onActivate(self):
        super(MovieItem, self)._onActivate()

        MovieIdle = self.Movies.get("Idle")
        MoviePick = self.Movies.get("Pick")

        if self.checkInteractive() is True:
            self.state = "Interactive"
        else:
            self.state = "UnInteractive"

        self.tc = TaskManager.createTaskChain(Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as source_repeat:
            Scopes = dict(
                Idle=Functor(self.__stateIdle, MovieIdle),
                Pick=Functor(self.__statePick, MoviePick),
                Enter=Functor(self.__stateEnter, MovieIdle),
                Leave=Functor(self.__stateLeave, MovieIdle),
                UnInteractive=Functor(self.__stateUnInteractive, MovieIdle),
                Interactive=Functor(self.__stateInteractive, MovieIdle),
            )

            def __states(isSkip, cb):
                cb(isSkip, self.state)
                pass

            with source_repeat.addRaceTask(2) as (source_scopes, source_semaphore):
                source_semaphore.addSemaphore(self.SemaphoreInteractive, Change=True)
                with source_semaphore.addIfSemaphore(self.SemaphoreInteractive, True) as (sem_true, sem_false):
                    sem_true.addFunction(self.__setState, "Interactive")

                    sem_false.addFunction(self.__setState, "UnInteractive")

                source_scopes.addScopeSwitch(Scopes, __states)

            # source_repeat.addScopeSwitch(Scopes, __states)
            pass
        pass

    def _onDeactivate(self):
        super(MovieItem, self)._onDeactivate()
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
            pass

        for mov in self.Movies.itervalues():
            mov.setEnable(False)
            pass

        self.SemaphoreInteractive.setValue(False)
        pass

    def _onFinalize(self):
        super(MovieItem, self)._onFinalize()

        for mov in self.Movies.itervalues():
            mov.onDestroy()
            pass

        self.Movies = {}
        self.SemaphoreInteractive = None
        pass

    pass
