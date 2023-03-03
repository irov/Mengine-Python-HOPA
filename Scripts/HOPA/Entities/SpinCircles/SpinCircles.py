from Foundation.TaskManager import TaskManager
from HOPA.SpinCirclesManager import SpinCirclesManager
from Notification import Notification

from Twist import Twist, MultiFinalTwist


Enigma = Mengine.importEntity("Enigma")


class SpinCircles(Enigma):
    MainTask = "Spin_Change_State"

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "TwistSaves")
        Type.addAction(Type, "IndicatorSaves")
        Type.addAction(Type, "MovieLoop")
        Type.addAction(Type, "Related")
        pass

    def __init__(self):
        super(SpinCircles, self).__init__()
        self.TwistCollection = {}
        self.PlayedSocket = None
        self.MovieWin = None
        self.hold = False
        self.isHold = True

        self.SocketEnter = None
        pass

    def _stopEnigma(self):
        super(SpinCircles, self)._stopEnigma()
        # self.saveTwists()

        self.removeViewNotify()
        if self.isHold is True:
            Notification.removeObserver(self.ButtonHold)
            pass

        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        return False
        pass

    def _onPreparation(self):
        super(SpinCircles, self)._onPreparation()
        self.SpinCircles = SpinCirclesManager.getSpinCircle(self.EnigmaName)
        self.disableAll()
        pass

    def disableAll(self):
        EnigmaObject, RotateItem, RotateInDepends, FinalState, DependRotate, \
            Indicators, MovieNames, MovieNamesRevert, Overs, isHold = self.SpinCircles.getParams()
        for movieNames in MovieNames:
            for movieName in movieNames:
                movie = self.object.getObject(movieName)
                movie.setEnable(False)
                pass
            pass

        for movieNames in MovieNamesRevert:
            for movieName in movieNames:
                movie = self.object.getObject(movieName)
                movie.setEnable(False)
                pass
            pass

        if self.object.hasObject("Movie_Win") is True:
            self.MovieWin = self.object.getObject("Movie_Win")
            self.MovieWin.setEnable(False)
            pass

        self.isHold = isHold
        pass

    def _onActivate(self):
        super(SpinCircles, self)._onActivate()
        if self.isHold is True:
            self.ButtonHold = Notification.addObserver(Notificator.onMouseButtonEvent, self.onHold)
            pass
        pass

    def _onDeactivate(self):
        super(SpinCircles, self)._onDeactivate()
        self.blockSockets(False)
        self.TwistCollection = {}
        self.PlayedSocket = None
        self.MovieWin = None
        self.hold = False
        self.isHold = True
        self.SocketEnter = None

        pass

    def _playEnigma(self):
        super(SpinCircles, self)._playEnigma()
        self.__DataPreparation()
        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Cb=self.__complete) as tc_m:
            with tc_m.addRepeatTask() as (tc_do, tc_until):
                SocketsName = self.TwistCollection.keys()
                with tc_do.addParallelTask(2) as (tc_al, tc_not):
                    tc_al.addTask("AliasSpinCircles", ObjectName=SocketsName[0], Sockets=SocketsName)
                    tc_not.addTask("TaskListener", ID=Notificator.onSpin, Filter=self.__Observe)
                    pass

                tc_do.addTask("TaskFunction", Fn=self.blockSockets, Args=(True,))
                tc_do.addTask("TaskFunction", Fn=self.PlayAction)

                tc_until.addTask("TaskListener", ID=Notificator.onSpinWin)
                pass
            tc_m.addTask("TaskFunction", Fn=self.blockSockets, Args=(True,))
            tc_m.addTask("TaskDelay", Time=1 * 1000)  # speed fix
            if self.MovieWin is not None:
                tc_m.addTask("TaskEnable", Object=self.MovieWin)
                tc_m.addTask("TaskMoviePlay", Movie=self.MovieWin)
                pass
            pass
        pass

    def getTwistCollection(self):
        return self.TwistCollection
        pass

    def __Observe(self, socket):
        if socket in self.TwistCollection:
            self.PlayedSocket = socket
            if self.isHold is True:
                self.hold = True
                pass
            return True
        return False
        pass

    def PlayAction(self):
        twist = self.TwistCollection[self.PlayedSocket]
        mainMovie = twist.next()
        dependMovies = twist.getDepends()
        dependMovies.append([mainMovie])
        movies = dependMovies

        tasks = len(movies)
        with TaskManager.createTaskChain(Name=SpinCircles.MainTask, Cb=self.isContinue) as tp:
            with tp.addParallelTask(tasks) as tci:
                for tc_p, movieList in zip(tci, movies):
                    Previous = None
                    for eachMovie in movieList:
                        if Previous is not None:
                            tc_p.addTask("TaskEnable", Object=Previous, Value=False)
                            pass
                        Previous = eachMovie
                        tc_p.addTask("TaskEnable", Object=eachMovie)
                        tc_p.addTask("TaskMoviePlay", Movie=eachMovie, Wait=True)
                        pass
                    pass
                pass

            tp.addTask("TaskNotify", ID=Notificator.onSpinMove, Args=(self.PlayedSocket,))
            tp.addTask("TaskFunction", Fn=self.isWin)
            tp.addTask("TaskFunction", Fn=self.blockSockets, Args=(False,))
            pass
        return True
        pass

    def isContinue(self, isSkip):
        if isSkip is True or self.hold is False:
            return
            pass
        if self.MovieLoop is False:
            return
            pass
        self.blockSockets(True)
        self.PlayAction()
        pass

    def onHold(self, event):
        """
        if hold button down on  socket state will be iterate next until button pressed
        """
        if event.isDown is False and self.hold is True:
            self.hold = False
            pass
        return False
        pass

    def __DataPreparation(self):
        EnigmaObject, RotateItem, RotateInDepends, FinalState, DependRotate, Indicators, \
            MovieNames, MovieNamesRevert, Overs, isHold = self.SpinCircles.getParams()  # unpacked
        self.EnigmaObject = EnigmaObject
        # Design Data
        for it, key in enumerate(RotateItem):
            if key in self.TwistCollection:
                continue
                pass
            MovieNames_Simple = []
            MovieNames_Revert = []

            for mov_N in MovieNames[it]:
                MovieNames_Simple.append(mov_N)
                pass

            for mov_N in MovieNamesRevert[it]:
                MovieNames_Revert.append(mov_N)
                pass

            MovieObjectsList = [self.object.getObject(item) for item in MovieNames_Simple if item is not None]
            MovieRevertObjectsList = []
            if (len(MovieNames_Revert) > 0):
                MovieRevertObjectsList = [self.object.getObject(item) for item in MovieNames_Revert if item is not None]

            if Indicators[it] is not None:
                IndicatorObj = self.object.getObject(Indicators[it])
                IndicatorObj.setEnable(False)
            else:
                IndicatorObj = None
            # ------>>

            if len(FinalState[it]) == 1:
                data = Twist(MovieObjectsList, MovieRevertObjectsList, FinalState[it][0], IndicatorObj)
            else:  # multiple final state
                data = MultiFinalTwist(MovieObjectsList, MovieRevertObjectsList, FinalState[it], IndicatorObj)
                pass
            # <---------
            self.TwistCollection[key] = data

            for movie in MovieObjectsList:
                movie.setEnable(False)

        # Build Depends

        for it, key in enumerate(RotateItem):
            dependKey = RotateInDepends[it]
            TwistDepObject = self.TwistCollection[dependKey]
            TwistObject = self.TwistCollection[key]
            rollTimes = DependRotate[it]
            TwistObject.setDepends(TwistDepObject, rollTimes)

        # if self.TwistSaves:
        #  for SockeKey in self.TwistSaves:
        #    twist = self.TwistCollection[SockeKey]
        #    state = self.TwistSaves[SockeKey]
        #   twist.setState(state)
        #   pass

        # Load Indicators:
        # if self.IndicatorSaves:
        #   [movie.setEnable(True) for movie in self.IndicatorSaves if self.IndicatorSaves[movie]]
        #  pass

        self.RestoreTwist()
        self.over_socket_preparation(Overs, RotateItem)  # customize
        pass

    def over_socket_preparation(self, overs, rotate_socket):
        if not overs:
            return
            pass
        over_movies = [self.object.getObject(movie_name) for movie_name in overs]
        socket_objects = [self.object.getObject(socket_name) for socket_name in rotate_socket]
        [movie.setEnable(False) for movie in over_movies]
        self.socket_views = dict(zip(socket_objects, over_movies))
        self.SocketEnter = Notification.addObserver(Notificator.onSocketMouseEnter, self.onSocketEntered)
        pass

    def onSocketEntered(self, socket_instance):
        TaskName = "SpinEnigmaView"
        if socket_instance in self.socket_views.keys():
            movie = self.socket_views.get(socket_instance)
            self.current_view = socket_instance
            if TaskManager.existTaskChain(TaskName):
                TaskManager.cancelTaskChain(TaskName)
                pass

            with TaskManager.createTaskChain(Name=TaskName) as tc:
                with tc.addRaceTask(2) as (tc_view, tc_leave):
                    tc_view.addTask("TaskEnable", Object=movie)
                    tc_view.addTask("TaskMoviePlay", Movie=movie, Loop=True)

                    tc_leave.addTask("TaskListener", ID=Notificator.onSocketMouseLeave, Filter=self.onLeaved)
                    tc_leave.addTask("TaskEnable", Object=movie, Value=False)
                    pass
                pass
            pass
        return False
        pass

    def onLeaved(self, socket_instance):
        if socket_instance == self.current_view:
            self.current_view = None
            return True
            pass
        return False
        pass

    def removeViewNotify(self):
        if self.SocketEnter is not None:
            Notification.removeObserver(self.SocketEnter)
            pass
        pass

    def RestoreTwist(self):
        for twist in self.TwistCollection.values():
            if twist.inFinalState():
                IndicatorMovie = twist.getIndicator()
                if IndicatorMovie is not None:
                    IndicatorMovie.setEnable(True)
                pass
            twist.enabler()
            firstMovie = twist.getCurentMovie()
            firstMovie.setEnable(True)
            MovieEn = firstMovie.getEntity()
            MovieEn.setFirstFrame()
            pass
        pass

    def blockSockets(self, blockBoolean):
        value = not blockBoolean
        for Socket in self.TwistCollection:
            SocketObj = self.object.getObject(Socket)
            SocketObj.setEnable(value)
            pass
        pass

    def __complete(self, isSkip):
        # self.setComplete()
        self.enigmaComplete()
        pass

    def isWin(self):
        self.updateIndicator()
        # print "=========================="
        # for key, twist in self.TwistCollection.iteritems():
        #    print "K", key, "T", twist
        #    pass
        FinalStates = [twist.inFinalState() for twist in self.TwistCollection.values()]
        FinalSetStates = set(FinalStates)
        if False in FinalSetStates:
            return False
            pass
        if len(FinalSetStates) == 1:
            if self.object.getRelated() is not True:
                Notification.notify(Notificator.onSpinWin)
                pass
            return True
            pass
        else:
            return False
            pass
        pass

    def _resetEnigma(self):
        movies = []
        for twist in self.TwistCollection.values():
            movies.append(twist.resetMovies())
            pass

        tasks = len(movies)
        with TaskManager.createTaskChain() as tc_res:
            with tc_res.addParallelTask(tasks) as tci:
                for tc_p, movieList in zip(tci, movies):
                    Previous = None
                    for eachMovie in movieList:
                        if Previous is not None:
                            tc_p.addTask("TaskEnable", Object=Previous, Value=False)
                            pass
                        Previous = eachMovie
                        tc_p.addTask("TaskEnable", Object=eachMovie)
                        tc_p.addTask("TaskMoviePlay", Movie=eachMovie, Wait=True)

    def _skipEnigma(self):
        if self.object.getPlay() is False:
            return False
        movies = []
        self.blockSockets(True)
        for twist in self.TwistCollection.values():
            movies.append(twist.skipMovies())
            pass
        tasks = len(movies)
        with TaskManager.createTaskChain() as tc_res:
            with tc_res.addParallelTask(tasks) as tci:
                for tc_p, movieList in zip(tci, movies):
                    Previous = None
                    for eachMovie in movieList:
                        if Previous is not None:
                            tc_p.addTask("TaskEnable", Object=Previous, Value=False)
                            pass
                        Previous = eachMovie
                        tc_p.addTask("TaskEnable", Object=eachMovie)
                        tc_p.addTask("TaskMoviePlay", Movie=eachMovie, Wait=True)
                        pass
                    pass
                pass
            tc_res.addTask("TaskFunction", Fn=self.updateIndicator)
            if self.MovieWin is not None:
                tc_res.addTask("TaskEnable", Object=self.MovieWin)
                tc_res.addTask("TaskMoviePlay", Movie=self.MovieWin)
                pass
            tc_res.addTask("TaskFunction", Fn=self.__complete, Args=(True,))
            pass
        return True
        pass

    def saveTwists(self):
        for socketKey in self.TwistCollection:
            twist = self.TwistCollection[socketKey]
            state = twist.getState()
            self.TwistSaves[socketKey] = state
            pass
        pass

    def updateIndicator(self):
        Movies = []
        for twist in self.TwistCollection.values():
            Movie = twist.getIndicator()
            if not Movie:
                continue
                pass
            if twist.inFinalState():
                if Movie.getEnable():
                    #                    Movie.setEnable(False)
                    if Movie not in Movies:
                        Movies.append(Movie)
                        pass
                    continue
                    pass
                Movie.setEnable(True)
                self.IndicatorSaves[Movie] = True
                Movies.append(Movie)
                pass
            else:
                Movie.setEnable(False)
                self.IndicatorSaves[Movie] = False
                pass

        if Movies:
            with TaskManager.createTaskChain() as tc:
                with tc.addParallelTask(len(Movies)) as tci:
                    for tc_p, movie in zip(tci, Movies):
                        tc_p.addTask("TaskMoviePlay", Movie=movie)

    def _restoreEnigma(self):
        self._playEnigma()
        pass
