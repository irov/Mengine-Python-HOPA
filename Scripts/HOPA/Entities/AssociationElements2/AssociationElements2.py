from Foundation.TaskManager import TaskManager

from AssociationElements2Manager import AssociationElements2Manager
from Element import Element

Enigma = Mengine.importEntity("Enigma")

class AssociationElements2(Enigma):
    def __init__(self):
        super(AssociationElements2, self).__init__()
        self.sockets = {}
        self.MovieSlot = None
        self.garbageEntities = []
        self.bufferElement = None
        self.BlockInput = False

        self.tc = None
        pass

    def _start(self):
        self.MovieSlot = self.object.getObject("Movie_Slot")
        MovieSlotEntity = self.MovieSlot.getEntity()
        Data = AssociationElements2Manager.getData(self.EnigmaName)
        for elementData in Data:
            name = elementData.getName()
            slotName = elementData.getSlotName()
            Slot = MovieSlotEntity.getMovieSlot(slotName)
            socketName = elementData.getSocketName()
            openMovieName = elementData.getOpenMovieName()
            openMovie = self.object.generateObject(openMovieName + slotName, openMovieName)
            openMovieEntityNode = openMovie.getEntityNode()
            Slot.addChild(openMovieEntityNode)
            closeMovieName = elementData.getCloseMovieName()
            closeMovie = self.object.generateObject(closeMovieName + slotName, closeMovieName)
            closeMovieEntityNode = closeMovie.getEntityNode()
            Slot.addChild(closeMovieEntityNode)
            activeMovieName = elementData.getActiveMovieName()
            activeMovie = self.object.generateObject(activeMovieName + slotName, activeMovieName)
            activeMovieEntityNode = activeMovie.getEntityNode()
            Slot.addChild(activeMovieEntityNode)
            self.garbageEntities.extend([openMovie, activeMovie, closeMovie])

            element = Element(name, openMovie, activeMovie, closeMovie)
            element.onPrepare()

            self.sockets[socketName] = element
            pass
        pass

    def _skipEnigma(self):
        for element in self.sockets.values():
            element.onActive()
            pass
        pass

    def _playEnigma(self):
        super(AssociationElements2, self)._playEnigma()
        self._start()
        # self.onMovieSocketClickObserver = Notification.addObserver(Notificator.onMovieSocketClick, self.__onMovieSocketClick)
        self.onWinObserver = Notification.addObserver(Notificator.onAssociationElementActive, self.__isComplete)

        self.tc = TaskManager.createTaskChain(Name="AssociationElements2_" + self.getName(), Repeat=True)

        with self.tc as tc:
            with tc.addRaceTaskList(self.sockets.keys()) as race_tcs:
                for socketName, tc_race in race_tcs:
                    tc_race.addTask("TaskMovieSocketClick", SocketName=socketName, Movie=self.MovieSlot)
                    tc_race.addFunction(self.onMovieSocketClick, socketName, self.MovieSlot)
                    pass
                pass
            pass

        pass

    def onMovieSocketClick(self, socketName, movieObject):
        if self.BlockInput is True:
            return False
            pass

        if movieObject is not self.MovieSlot:
            return False
            pass

        element = self.sockets[socketName]

        if element.getBlocked() is True:
            return False
            pass

        self.__turnManage(element)

        return False
        pass

    # def __onMovieSocketClick(self,touchId, button, isDown, movieObject, hotspot, socketName):
    #     if self.BlockInput is True:
    #         return False
    #         pass
    #     if movieObject is not self.MovieSlot:
    #         return False
    #         pass
    #     if isDown is False:
    #         return False
    #         pass
    #     element = self.sockets[socketName]
    #     if element.getBlocked() is True:
    #         return False
    #         pass
    #     self.__turnManage(element)
    #     return False
    #     pass

    def _stopEnigma(self):
        super(AssociationElements2, self)._stopEnigma()
        Notification.removeObserver(self.onWinObserver)
        # Notification.removeObserver(self.onMovieSocketClickObserver)

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
            pass

        pass

    def __turnManage(self, element):
        if element is self.bufferElement:
            element.onClose()
            self.bufferElement = None
            return
            pass
        if self.bufferElement is None:
            self.bufferElement = element
            element.onOpen()
            return
        element.onOpen(self.bufferElement)
        self.bufferElement = None
        return
        pass

    def __isComplete(self):
        for element in self.sockets.values():
            if element.getActive() is False:
                return False
                pass
            continue
            pass
        self.enigmaComplete()
        return True
        pass

    def _resetEnigma(self):
        for element in self.sockets.values():
            if element.getOpen() is True:
                element.onClose()
                pass
            pass
        return
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _onDeactivate(self):
        super(AssociationElements2, self)._onDeactivate()
        for movie in self.garbageEntities:
            movie.onDestroy()
            pass

        self.garbageEntities = []

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
            pass
        pass

    pass
