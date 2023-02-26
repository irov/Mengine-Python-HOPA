from Foundation.TaskManager import TaskManager

class Wheel(object):
    SLOT = "container"
    TaskName = "Programttor_Wheel"

    def __init__(self, moviesUp, moviesDown, transferObject):
        self.moviesUp = moviesUp
        self.moviesDown = moviesDown
        self._cursor = 0
        self.transferChild = transferObject.getEntity()
        self.currentMovie = None
        self.slotCS = Wheel.SLOT
        self._onInitialize()
        pass

    def onDeactivate(self):
        if TaskManager.existTaskChain(Wheel.TaskName):
            TaskManager.cancelTaskChain(Wheel.TaskName)
            pass

        self.transferChild.removeFromParent()
        pass

    def _onInitialize(self):
        [mov.setEnable(False) for mov in self.moviesDown]
        [mov.setEnable(False) for mov in self.moviesUp]
        movDown = self.moviesDown[self._cursor]
        movDown.setEnable(True)
        self.currentMovie = movDown
        self.__addChild(movDown)
        pass

    def moveUp(self):
        if self._cursor == 0:
            return
            pass

        if TaskManager.existTaskChain(Wheel.TaskName):
            return
            pass

        self._cursor -= 1
        mov = self.moviesUp[self._cursor]
        self.__addChild(mov)
        with TaskManager.createTaskChain(Name=Wheel.TaskName) as tc:
            tc.addTask("TaskMoviePlay", Movie=mov)
            pass
        pass

    def moveDown(self, finalMethod):
        if self._cursor == len(self.moviesUp):
            return
            pass

        if TaskManager.existTaskChain(Wheel.TaskName):
            return
            pass

        mov = self.moviesDown[self._cursor]
        self._cursor += 1

        self.__addChild(mov)
        with TaskManager.createTaskChain(Name=Wheel.TaskName) as tc:
            tc.addTask("TaskMoviePlay", Movie=mov)
            if len(self.moviesDown) == self._cursor and finalMethod is not None:
                tc.addTask("TaskFunction", Fn=finalMethod)
            pass
        pass

    def __addChild(self, movie):
        movie.setEnable(True)
        movieEntity = movie.getEntity()
        slotNode = movieEntity.getMovieSlot(self.slotCS)
        slotNode.addChild(self.transferChild)
        Object = self.transferChild.getObject()
        Object.setPosition((0, 0))
        if movie is not self.currentMovie:
            self.currentMovie.setEnable(False)
            self.currentMovie = movie
            pass
        pass

    pass