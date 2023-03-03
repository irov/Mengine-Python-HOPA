import math

from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager


class Planet(Initializer):
    SOCKET_NAME = "Socket_Planet"

    def __init__(self, enigmaObject, initialData):
        super(Planet, self).__init__()
        self.enigmaObject = enigmaObject
        self.socket = None
        self.movieName = None
        self.movie = None
        self.duration = 0
        self.startTiming = 0
        self.currentTiming = 0
        self.arrowPos = None
        self.startPos = None
        self.initialData = initialData
        pass

    def onInitialize(self):
        self.movieName = self.initialData.getMovieName()
        self.movie = self.enigmaObject.getObject(self.movieName)
        self.movie.setEnable(True)

        self.socket = self.enigmaObject.generateObject("Internal_Socket_%s" % (self.movieName), Planet.SOCKET_NAME)
        self.socketEntity = self.socket.getEntity()
        self.socketEntity.setEventListener(onGlobalHandleMouseMove=self._onGlobalMouseMove)
        self.socketEntity.enableGlobalMouseEvent(False)

        MovieEntity = self.movie.getEntity()
        MovieSlot = MovieEntity.getMovieSlot("planet")
        MovieSlot.addChild(self.socketEntity)

        self.duration = self.movie.getDuration()
        self.degree = self.duration / (2 * math.pi)
        worldPos = MovieSlot.getWorldPosition()
        anchorPos = MovieSlot.getOrigin()
        self.centreVec = (worldPos.x + anchorPos.x, worldPos.y + anchorPos.y)

        planetSave = self.enigmaObject.getPlanets()
        if self.movieName in planetSave.keys():
            startTiming = planetSave[self.movieName]
            MovieEntity.setTiming(startTiming)
            self.currentTiming = startTiming
            pass
        else:
            startTiming = self.initialData.getStartTiming()
            MovieEntity.setTiming(startTiming)
            self.currentTiming = startTiming
            pass

        self.startTiming = self.initialData.getStartTiming()
        self.addPlanet()
        self.playTasks()
        pass

    def _onGlobalMouseMove(self, touchId, x, y, dx, dy):
        self.arrowPos = Mengine.getCursorPosition()
        pass

    def playTasks(self):
        if TaskManager.existTaskChain(self.movieName):
            TaskManager.cancelTaskChain(self.movieName)
            pass

        with TaskManager.createTaskChain(Name=self.movieName, Repeat=True) as tc_play:
            tc_play.addTask("TaskSocketClick", Socket=self.socket)
            tc_play.addTask("TaskFunction", Fn=self.enableGlobalEvent, Args=(True,))

            with tc_play.addRepeatTask() as (tc_move, tc_up):
                tc_move.addTask("TaskMouseMoveDistance", Distance=0)
                tc_move.addTask("TaskFunction", Fn=self.updateMovie)

                tc_up.addTask("TaskMouseButtonClick", isDown=False)
                tc_up.addTask("TaskFunction", Fn=self.enableGlobalEvent, Args=(False,))
                tc_up.addTask("TaskFunction", Fn=self.addPlanet)
                tc_up.addTask("TaskFunction", Fn=self.playTasks)
                pass
            pass
        pass

    def addPlanet(self):
        self.enigmaObject.changeParam("Planets", self.movieName, self.currentTiming)
        pass

    def enableGlobalEvent(self, value):
        if value is True:
            self.startPos = Mengine.getCursorPosition()
            self.arrowPos = Mengine.getCursorPosition()
            pass
        self.socketEntity.enableGlobalMouseEvent(value)
        return True
        pass

    def updateMovie(self):
        x0 = self.centreVec[0]
        y0 = self.centreVec[1]
        x1 = self.startPos.x - x0
        y1 = self.startPos.y - y0
        x2 = self.arrowPos.x - x0
        y2 = self.arrowPos.y - y0

        v = (x1 * x2 + y1 * y2) / pow((pow(x1, 2) + pow(y1, 2)) * (pow(x2, 2) + pow(y2, 2)), 0.5)
        cos = round(v, 13)
        value = math.acos(cos)
        increase = value * self.degree
        increase_timing = round(increase)

        dt = x1 * y2 - y1 * x2
        if dt > 0:
            leftTurn = -1
            pass
        else:
            leftTurn = 1
            pass

        MovieEn = self.movie.getEntity()
        current_timing = MovieEn.getTiming()
        set_time = current_timing + increase_timing * leftTurn

        if set_time >= self.duration:
            set_time = set_time - self.duration
            MovieEn.setTiming(self.duration)
            MovieEn.setTiming(set_time)
            pass
        elif set_time <= 0:
            set_time = self.duration + set_time
            MovieEn.setTiming(self.duration)
            MovieEn.setTiming(set_time)
        else:
            MovieEn.setTiming(set_time)
            pass
        self.currentTiming = set_time
        self.startPos = self.arrowPos
        return True
        pass

    def resetPlanet(self):
        MovieEntity = self.movie.getEntity()
        MovieEntity.setTiming(self.startTiming)
        self.currentTiming = self.startTiming
        self.addPlanet()
        pass

    def onFinalize(self):
        self.socket.removeFromParent()
        pass

    pass
