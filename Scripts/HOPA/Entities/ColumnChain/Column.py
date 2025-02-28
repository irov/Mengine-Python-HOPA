from Foundation.TaskManager import TaskManager


class Column(object):
    def __init__(self, data, enigma):
        self.data = data
        self.enigma = enigma
        self.columnName = None
        self.currentState = None
        self.currentMovie = None
        self.currentMovieIndex = None
        self.isMovingUp = True
        self.statesLength = None
        self.winState = None
        self.MovieObjectList = []

        self.preparation()
        pass

    def preparation(self):
        self.columnName = self.data.getColumnName()
        self.currentState = self.data.getStartState()
        self.statesLength = self.data.getStatesLength()
        self.winState = self.data.getWinState()
        movieNames = self.data.getMovieObjectNameList()
        for movieName in movieNames:
            movieObject = self.enigma.getObject(movieName)
            movieObject.setEnable(False)
            self.MovieObjectList.append(movieObject)
            pass
        self.currentMovieIndex = self.currentState - 1
        self.currentMovie = self.MovieObjectList[self.currentMovieIndex]
        self.currentMovie.setEnable(True)
        self.currentMovie.setLastFrame(False)
        pass

    def columnUpdate(self, socket):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskInteractive", Object=socket, Value=False)
            tc.addTask("TaskMoviePlay", Movie=self.currentMovie)
            tc.addDisable(self.currentMovie)
            tc.addFunction(self.columnRefreshing)
            tc.addNotify(Notificator.onColumnPlaced)
            tc.addTask("TaskInteractive", Object=socket, Value=True)
            pass
        pass

    def columnRefreshing(self):
        newCurrentMovieIndex = self.currentMovieIndex + 1
        if newCurrentMovieIndex == len(self.MovieObjectList):
            newCurrentMovieIndex = 0
            pass

        newCurrentMovie = self.MovieObjectList[newCurrentMovieIndex]
        newCurrentMovie.setEnable(True)

        self.currentMovie.setEnable(False)
        self.currentMovieIndex = newCurrentMovieIndex
        self.currentMovie = newCurrentMovie
        self.currentMovie.setLastFrame(False)

        if self.isMovingUp is True:
            self.currentState += 1
            if self.currentState > self.statesLength:
                self.currentState = self.statesLength - 1
                self.isMovingUp = False
                pass
            pass
        else:
            self.currentState -= 1
            if self.currentState < 1:
                self.currentState = 2
                self.isMovingUp = True
                pass
            pass
        pass

    def isWinState(self):
        if self.currentState == self.winState:
            return True
            pass
        return False
