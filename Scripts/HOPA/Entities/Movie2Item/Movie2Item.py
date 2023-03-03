from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager


class Movie2Item(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "CompositionNameIdle")
        Type.addAction(Type, "CompositionNamePick")

        Type.addAction(Type, "ResourceMovie")

    def __init__(self):
        super(Movie2Item, self).__init__()
        self.tc = None
        self.state = "Idle"

        self.Movies = {}

        self.SemaphoreInteractive = Semaphore(False, "Interactive")

    def getCurrentMovie(self):
        if self.state not in self.Movies:
            return None

        Movie = self.Movies.get(self.state)

        if Movie is None:
            return None

        return Movie

    def getCurrentEnabledMovie(self):
        for Movie in self.Movies.itervalues():
            if Movie.getEnable() is True:
                return Movie

        return None

    def getHintPoint(self):
        CurrentMovie = self.getCurrentEnabledMovie()
        if CurrentMovie is None:
            return Mengine.vec2f(0.0, 0.0)

        if CurrentMovie.hasSlot('hint') is True:
            slot = CurrentMovie.getMovieSlot('hint')

            Point = slot.getWorldPosition()
        else:
            MovieSocket = CurrentMovie.getSocket('socket')

            Point = MovieSocket.getWorldPolygonCenter()

        if Point is None:
            return Mengine.vec2f(0.0, 0.0)

        return Point

    def _onInitialize(self, obj):
        super(Movie2Item, self)._onInitialize(obj)

        if self.ResourceMovie is None:
            return False

        if Mengine.hasResource(self.ResourceMovie) is False:
            return False

        resource = Mengine.getResourceReference(self.ResourceMovie)

        if resource is None:
            Trace.log("Entity", 0, "Movie2Item._onInitialize: not found resource %s" % (resource))
            return False

        def __createMovie(name, comp, play, loop):
            if resource.hasComposition(comp) is False:
                # print "Movie2Item.__createMovie: resource.hasComposition(comp) is False", name, self.getName()
                return None

            mov = ObjectManager.createObjectUnique("Movie2", name, self.object, ResourceMovie=resource, CompositionName=comp)

            if mov is None:
                return None

            mov.setEnable(False)
            mov.setPlay(play)
            mov.setLoop(loop)

            movEntityNode = mov.getEntityNode()
            self.addChild(movEntityNode)

            self.Movies[name] = mov

            return mov
            pass

        __createMovie("Idle", self.CompositionNameIdle, True, True)
        __createMovie("Pick", self.CompositionNamePick, False, False)

        return True

    def getPickEffectMovie(self, AttachNode):
        ResourceMovie, CompositionName = self.getPickEffectResourceName()
        MovieName = "Movie2ItemPickEffect_{}".format(CompositionName)

        if ResourceMovie is None:
            return None
        if CompositionName is None:
            return None

        Movie = ObjectManager.createObjectUnique("Movie2", MovieName, None, ResourceMovie=ResourceMovie, CompositionName=CompositionName)

        Movie.setEnable(True)
        Movie.setPlay(False)
        Movie.setLoop(False)
        Movie.setLastFrame(True)

        resource_movie = Movie.getResourceMovie()
        if resource_movie.hasCompositionLayer(CompositionName, "Shadow"):
            Movie.appendParam("DisableLayers", "Shadow")

        MovieEntityNode = Movie.getEntityNode()
        AttachNode.addChild(MovieEntityNode)

        return Movie

    def getPickEffectResourceName(self):
        if "Pick" in self.Movies:
            return (self.ResourceMovie, self.CompositionNamePick)

        if "Idle" in self.Movies:
            return (self.ResourceMovie, self.CompositionNameIdle)

        return None

    def _updateInteractive(self, value):
        self.SemaphoreInteractive.setValue(value)

    def __setState(self, state):
        # print " [MovieItem] state", self.getName(), state
        self.state = state

    def smartEnableMovie(self, MovieToEnable):
        if MovieToEnable.getEnable() is True:
            return

        for Movie in self.Movies.itervalues():
            if Movie is not MovieToEnable:
                Movie.setEnable(False)

        MovieToEnable.setEnable(True)

    def _scopeMovie2SocketClick(self, source, movie2_object, socket_name):
        socket = movie2_object.getSocket(socket_name)

        source.addTask("TaskNodeSocketClick", Socket=socket, isDown=True)

    def _scopeMovie2SocketEnter(self, source, movie2_object, socket_name):
        socket = movie2_object.getSocket(socket_name)

        source.addTask("TaskNodeSocketEnter", Socket=socket)

    def _scopeMovie2SocketLeave(self, source, movie2_object, socket_name):
        socket = movie2_object.getSocket(socket_name)

        source.addTask("TaskNodeSocketLeave", Socket=socket)

    def __stateIdle(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)

        with source.addRaceTask(2) as (source_click, source_enter):
            source_click.addScope(self._scopeMovie2SocketClick, MovieIdle, 'socket')

            source_click.addScope(self._scopePick)

            source_enter.addScope(self._scopeMovie2SocketEnter, MovieIdle, 'socket')
            source_enter.addFunction(self.__setState, "Enter")

    def _scopePick(self, source):
        if ArrowManager.emptyArrowAttach() is True:
            source.addTask("AliasEnergyConsume", Action="PickItem", Cb=self.__setState, CbArgs=["Pick"])

    def __stateEnter(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)

        source.addNotify(Notificator.onMovieItemEnter, self.object)

        with source.addRaceTask(2) as (source_click, source_leave):
            source_click.addScope(self._scopeMovie2SocketClick, MovieIdle, 'socket')
            source_click.addNotify(Notificator.onMovieItemLeave, self.object)

            source_click.addScope(self._scopePick)

            source_leave.addScope(self._scopeMovie2SocketLeave, MovieIdle, 'socket')
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

        source.addFunction(self.smartEnableMovie, MoviePick)

        source.addNotify(Notificator.onMovieItemClick, self.object)
        source.addTask("TaskMovie2Play", Movie2=MoviePick)
        source.addNotify(Notificator.onMovieItemPick, self.object)
        source.addBlock()

    def _movie2SocketEnable(self, movie2_object, socket_name, enable):
        socket = movie2_object.getSocket(socket_name)

        if enable:
            socket.enable()
        else:
            socket.disable()

    def __stateInteractive(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)
        source.addFunction(self._movie2SocketEnable, MovieIdle, 'socket', True)

        source.addFunction(self.__setState, "Idle")

    def __stateUnInteractive(self, source, MovieIdle):
        source.addFunction(self.smartEnableMovie, MovieIdle)
        source.addFunction(self._movie2SocketEnable, MovieIdle, 'socket', False)

        source.addBlock()

    def checkInteractive(self):
        return self.object.getParam("Interactive") > 0

    def _onActivate(self):
        super(Movie2Item, self)._onActivate()

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

            with source_repeat.addRaceTask(2) as (source_scopes, source_semaphore):
                source_semaphore.addSemaphore(self.SemaphoreInteractive, Change=True)
                with source_semaphore.addIfSemaphore(self.SemaphoreInteractive, True) as (sem_true, sem_false):
                    sem_true.addFunction(self.__setState, "Interactive")

                    sem_false.addFunction(self.__setState, "UnInteractive")

                source_scopes.addScopeSwitch(Scopes, __states)

    def _onDeactivate(self):
        super(Movie2Item, self)._onDeactivate()

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for mov in self.Movies.itervalues():
            mov.setEnable(False)

        self.SemaphoreInteractive.setValue(False)

    def _onFinalize(self):
        super(Movie2Item, self)._onFinalize()

        for mov in self.Movies.itervalues():
            mov.onDestroy()

        self.Movies = {}
        self.SemaphoreInteractive = None
