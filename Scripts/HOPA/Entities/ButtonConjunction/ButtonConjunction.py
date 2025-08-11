from Foundation.TaskManager import TaskManager

from ButtonConjunctionManager import ButtonConjunctionManager
from MoviesButton import MoviesButton

Enigma = Mengine.importEntity("Enigma")

class ButtonConjunction(Enigma):

    def __init__(self):
        super(ButtonConjunction, self).__init__()
        self.socketToButton = {}
        self.orderedToClick = []
        self.restToClick = []
        self.make_reset = False
        self.current_view = None
        pass

    def _stopEnigma(self):
        Notification.removeObserver(self.SocketHandler)
        Notification.removeObserver(self.SocketEnterHandler)
        pass

    def _skipEnigma(self):
        self._complete(True)
        pass

    def _playEnigma(self):
        self.SocketHandler = Notification.addObserver(Notificator.onSocketClick, self.on_socket_click)
        self.SocketEnterHandler = Notification.addObserver(Notificator.onSocketMouseEnter, self.on_mouse_enter)
        self.restore()
        pass

    def restore(self):
        collection = ButtonConjunctionManager.getCollection(self.EnigmaName)
        moviesActivate = collection.getMoviesActive()
        moviesDown = collection.getMoviesDown()
        moviesOver = collection.getMoviesOver()
        sockets = collection.getSockets()
        moviesActivateObjects = [self.object.getObject(name) for name in moviesActivate]
        moviesDownObjects = [self.object.getObject(name) for name in moviesDown]
        moviesOverObjects = [self.object.getObject(name) for name in moviesOver]
        socketObjects = [self.object.getObject(name) for name in sockets]
        self.orderedToClick = socketObjects
        movie_stack = zip(moviesActivateObjects, moviesDownObjects, moviesOverObjects)
        for i, movies_tuple in enumerate(movie_stack):
            _socket = socketObjects[i]
            buttonInstance = MoviesButton(*movies_tuple)
            self.socketToButton[_socket] = buttonInstance
            pass
        self.restToClick = self.orderedToClick[:]
        [socket.setInteractive(True) for socket in socketObjects]
        pass

    def on_socket_click(self, socket):
        if socket in self.socketToButton:
            self.step_socket = socket
            MovieButton = self.socketToButton[socket]
            socket.setInteractive(False)
            MovieButton.push(self.step_valid)
            planedToClick = self.restToClick.pop(0)
            if planedToClick == socket:
                if self.restToClick == []:
                    self._complete(True)
                    pass
                pass
            else:
                self.make_reset = True
                self.restToClick = self.orderedToClick[:]
                pass
            pass
        return False
        pass

    def step_valid(self, *args):
        if self.make_reset is True:
            self.make_reset = False
            self.resetAll()
            pass
        return False
        pass

    def resetAll(self):
        # worth it
        [socket.setInteractive(True) for socket in self.socketToButton.keys() if socket.getInteractive() == 0]
        for button in self.socketToButton.values():
            button.reset()
            pass
        pass

    def _resetEnigma(self):
        self.resetAll()
        self.restToClick = self.orderedToClick[:]
        pass

    def on_mouse_enter(self, socket):
        TaskName = "ButtonEnter"
        if socket in self.socketToButton:
            button = self.socketToButton[socket]
            _movie = button.getMovieOver()
            PrevButton = self.socketToButton.get(self.current_view)
            if PrevButton is not None:
                prev_movie = PrevButton.getMovieOver()
                prev_movie.setEnable(False)
                pass
            self.current_view = socket
            self.cancelOverView()
            with TaskManager.createTaskChain(Name=TaskName) as tc:
                with tc.addRaceTask(2) as (tc_view, tc_leave):
                    tc_view.addEnable(_movie)
                    tc_view.addTask("TaskMoviePlay", Movie=_movie, Loop=True)
                    tc_leave.addListener(Notificator.onSocketMouseLeave, Filter=self.onLeaved)
                    tc_leave.addDisable(_movie)
                    pass
                pass
            pass
        return False
        pass

    def _complete(self, isSkip):
        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass

    def cancelOverView(self):
        TaskName = "ButtonEnter"
        if TaskManager.existTaskChain(TaskName):
            TaskManager.cancelTaskChain(TaskName)
            pass
        pass

    def onLeaved(self, socket_instance):
        if socket_instance == self.current_view:
            self.current_view = None
            return True
            pass
        return False
        pass
