from Foundation.TaskManager import TaskManager

from Element import Element
from LightLockManager import LightLockManager

Enigma = Mengine.importEntity("Enigma")

class LightLock(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(LightLock, self).__init__()
        self.sockets = {}
        self.LastSocket = None
        self.checkSocket = None
        self.winCheckList = []
        pass

    def _stopEnigma(self):
        super(LightLock, self)._stopEnigma()
        pass
    def _resetEnigma(self):
        pass

    def _onPreparation(self):
        super(LightLock, self)._onPreparation()
        InitData = LightLockManager.getLightLock(self.EnigmaName)

        socketData = InitData.getSocketData()
        for socketName, keys in socketData.iteritems():
            element = Element(self.object, keys)
            socket = self.object.getObject(socketName)
            socket.setInteractive(True)
            for value, movieName in keys.iteritems():
                movie = self.object.getObject(movieName)
                movie.setEnable(False)
                pass
            self.sockets[socket] = element
            pass

        waitData = InitData.getWaitData()
        for socketName, keys in waitData.iteritems():
            socket = self.object.getObject(socketName)
            element = self.sockets[socket]
            element.setWaitData(keys)
            for value, movieName in keys.iteritems():
                movie = self.object.getObject(movieName)
                movie.setEnable(False)
                pass
            pass

        stateData = InitData.getStateData()
        for socketName, value in stateData.iteritems():
            socket = self.object.getObject(socketName)
            element = self.sockets[socket]
            element.setValue(value)
            pass

        winMoviesData = InitData.getWinMoviesData()
        for movieName, data in winMoviesData.iteritems():
            movie = self.object.getObject(movieName)
            movie.setEnable(False)
            pass

        slotData = InitData.getSlotData()
        fieldMovie = self.object.getObject("Movie_Field")
        fieldMovieEntity = fieldMovie.getEntity()
        for socketName, value in slotData.iteritems():
            socket = self.object.getObject(socketName)
            element = self.sockets[socket]
            movieSelect = self.object.generateObject("Movie_%s" % (socketName,), "Movie_Selected")
            movieSelect.setEnable(False)
            slot = fieldMovieEntity.getMovieSlot(value)
            movieEntity = movieSelect.getEntity()
            slot.addChild(movieEntity)
            element.setSelectMovie(movieSelect)
            pass
        pass

    def _onActivate(self):
        super(LightLock, self)._onActivate()
        fieldMovie = self.object.getObject("Movie_Field")
        fieldMovie.setEnable(True)
        pass

    def _onDeactivate(self):
        super(LightLock, self)._onDeactivate()
        for element in self.sockets.values():
            element.onDestroy()
            pass
        pass

    def __playTasks(self):
        if TaskManager.existTaskChain(self.EnigmaName) is True:
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        with TaskManager.createTaskChain(Name=self.EnigmaName) as tc:
            tc.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.__gameSocket)
            tc.addTask("TaskFunction", Fn=self.isWinPosition)
            tc.addTask("TaskFunction", Fn=self.isWin)
            pass
        pass

    def __gameSocket(self, curSocket):
        if curSocket not in self.sockets.keys():
            return False
            pass
        if self.LastSocket is None:
            self.LastSocket = curSocket
            element = self.sockets[curSocket]
            element.onSelect()
            return True
            pass
        if curSocket is self.LastSocket:
            element = self.sockets[curSocket]
            element.onDeselect()
            self.LastSocket = None
            return True
            pass
        else:
            element = self.sockets[curSocket]
            element.onSelect()

            element2 = self.sockets[self.LastSocket]
            element2.onSelect()

            self.swapElements(element, element2)
            element2.onDeselect()
            element.onDeselect()
            self.LastSocket = None
            return True
            pass
        return True
        pass

    def swapElements(self, first, second):
        swapValue1 = first.getValue()
        swapValue2 = second.getValue()

        first.setValue(swapValue2)
        second.setValue(swapValue1)
        pass

    def isWinPosition(self):
        InitData = LightLockManager.getLightLock(self.EnigmaName)
        winParam = InitData.getWinParam()
        winMoviesData = InitData.getWinMoviesData()
        for movieName, socketPair in winMoviesData.iteritems():
            socketName1 = socketPair[0]
            socketName2 = socketPair[1]
            socket1 = self.object.getObject(socketName1)
            socket2 = self.object.getObject(socketName2)
            element1 = self.sockets[socket1]
            element2 = self.sockets[socket2]
            value1 = element1.getValue()
            value2 = element2.getValue()

            movieWin = self.object.getObject(movieName)
            if (value1, value2) in winParam:
                movieWin.setEnable(True)
                movieWin.setLoop(True)
                movieWin.setPlay(True)
                element2.setIsWinPos(True)
                element1.setIsWinPos(True)
                element2.setActivate(True)
                element1.setActivate(True)
                pass
            elif (value2, value1) in winParam:
                movieWin.setEnable(True)
                movieWin.setLoop(True)
                movieWin.setPlay(True)
                element2.setIsWinPos(True)
                element1.setIsWinPos(True)
                element2.setActivate(True)
                element1.setActivate(True)
            else:
                movieWin.setPlay(False)
                movieWin.setEnable(False)
                element2.setIsWinPos(False)
                element1.setIsWinPos(False)
                element2.setActivate(False)
                element1.setActivate(False)
                pass
            pass
        pass

    def isWin(self):
        for socket, element in self.sockets.iteritems():
            if element.getIsWinPos() is True:
                continue
                pass
            else:
                self.__playTasks()
                return False
                pass
            pass

        self.enigmaComplete()
        return True
        pass

    def _playEnigma(self):
        self.isWinPosition()
        self.__playTasks()
        pass

    pass