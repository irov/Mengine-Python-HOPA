from Foundation.TaskManager import TaskManager
from Notification import Notification

from RotateAndReflectElementManager import RotateAndReflectElementManager


Enigma = Mengine.importEntity("Enigma")


class RotateAndReflectElement(Enigma):
    Slots = [
        "slot1", "slot2", "slot3", "slot4", "slot5", "slot6", "slot7", "slot8", "slot9", "slot10", "slot11", "slot12"
    ]

    def __init__(self):
        super(RotateAndReflectElement, self).__init__()
        self.PositionMovie = None
        self.RotateMovie = None
        self.Trigger = None
        self.sockets = {}
        self.swap = {}
        self.sprites = {}
        self.SocketObserver = None
        self.ButtonObserver = None
        pass

    def _onInitialize(self, obj):
        super(RotateAndReflectElement, self)._onInitialize(obj)

        if _DEVELOPMENT is True:
            if self.object.hasObject("Movie_Position") is False:
                self.initializeFailed("RotateAndReflectElement dont has Movie_Position")
                pass
            pass
        pass

    def _stopEnigma(self):
        super(RotateAndReflectElement, self)._stopEnigma()
        Notification.removeObserver(self.SocketObserver)
        Notification.removeObserver(self.ButtonObserver)
        self.SocketObserver = None
        self.ButtonObserver = None
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _playEnigma(self):
        self.SocketObserver = Notification.addObserver(Notificator.onSocketClick, self.__onSocketClick)
        self.ButtonObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def __onButtonClick(self, button):
        if button is not self.Trigger:
            return False
            pass
        self.rotateElements()
        return False
        pass

    def __onSocketClick(self, curSocket):
        if curSocket not in self.sockets:
            return False
            pass
        swapMovie = self.sockets[curSocket]

        self.swapElements(swapMovie)
        return False
        pass

    def isWin(self):
        for sprite, tuple in self.sprites.iteritems():
            if tuple[0] != tuple[1]:
                return False
                pass
            continue
            pass
        return True
        pass

    def rotateElements(self):
        for Sprite, tuple in self.sprites.iteritems():
            spE = Sprite.getEntity()
            spEntityNode = Sprite.getEntityNode()
            spE.removeFromParent()
            curPos = tuple[0]
            movieEn = self.RotateMovie.getEntity()
            slot = movieEn.getMovieSlot(curPos)
            slot.addChild(spEntityNode)
            index = self.Slots.index(curPos)
            index += 1
            if index == len(self.Slots):
                index = 0
                pass
            newPos = self.Slots[index]
            tuple[0] = newPos

            pass

        def __update(isSkip):
            for Sprite, tuple in self.sprites.iteritems():
                spE = Sprite.getEntity()
                spEntityNode = Sprite.getEntityNode()
                spE.removeFromParent()
                curPos = tuple[0]
                movieEn = self.PositionMovie.getEntity()
                slot = movieEn.getMovieSlot(curPos)
                slot.addChild(spEntityNode)
                pass
            if self.isWin() is True:
                self.enigmaComplete()
                pass
            pass

        if TaskManager.existTaskChain("Rotate") is True:
            TaskManager.cancelTaskChain("Rotate")
            pass

        with TaskManager.createTaskChain(Name="Rotate", Cb=__update) as tc:
            tc.addFunction(self.enableSockets, False)
            tc.addTask("TaskMoviePlay", Movie=self.RotateMovie, Wait=True)
            tc.addFunction(self.enableSockets, True)
            pass
        pass

    def enableSockets(self, value):
        for socket in self.sockets:
            socket.setInteractive(value)
            pass
        self.Trigger.setInteractive(value)

        pass

    def swapElements(self, swapMovie):
        value = self.swap[swapMovie]
        swapMovie.setEnable(True)
        swapMovieEn = swapMovie.getEntity()

        for Sprite, tuple in self.sprites.iteritems():
            if tuple[0] == value[0]:
                spEn = Sprite.getEntity()
                spEntityNode = Sprite.getEntityNode()
                spEn.removeFromParent()
                slot = swapMovieEn.getMovieSlot(value[0])
                slot.addChild(spEntityNode)
                tuple[0] = value[1]
                continue
                pass
            if tuple[0] == value[1]:
                spEn = Sprite.getEntity()
                spEntityNode = Sprite.getEntityNode()
                spEn.removeFromParent()
                slot = swapMovieEn.getMovieSlot(value[1])
                slot.addChild(spEntityNode)
                tuple[0] = value[0]
                continue
                pass
            pass

        def __update(isSkip):
            for Sprite, tuple in self.sprites.iteritems():
                spE = Sprite.getEntity()
                spEntityNode = Sprite.getEntityNode()
                spE.removeFromParent()
                curPos = tuple[0]
                movieEn = self.PositionMovie.getEntity()
                slot = movieEn.getMovieSlot(curPos)
                slot.addChild(spEntityNode)
                pass
            swapMovie.setEnable(False)

            if self.isWin() is True:
                self.enigmaComplete()
                pass
            pass

        if TaskManager.existTaskChain("Swap") is True:
            TaskManager.cancelTaskChain("Swap")
            pass

        with TaskManager.createTaskChain(Name="Swap", Cb=__update) as tc:
            tc.addFunction(self.enableSockets, False)
            tc.addTask("TaskMoviePlay", Movie=swapMovie, Wait=True)
            tc.addFunction(self.enableSockets, True)
            pass
        pass

        pass

    def _onPreparation(self):
        super(RotateAndReflectElement, self)._onPreparation()

        Data = RotateAndReflectElementManager.getData(self.EnigmaName)
        self.RotateMovie = self.object.getObject("Movie_Circle")
        self.RotateMovie.setEnable(True)

        self.PositionMovie = self.object.getObject("Movie_Position")
        self.PositionMovie.setEnable(True)

        self.Trigger = self.object.getObject("Button_Trigger")
        self.Trigger.setInteractive(True)

        elementsData = Data.getElement()

        for id, element in elementsData.iteritems():
            SpriteName = element.getSprite()
            Sprite = self.object.getObject(SpriteName)
            Sprite.setOrigin((0, 0))
            Sprite.setPosition((0, 0))
            StartPos = element.getStartPos()
            WinPos = element.getWinPos()
            entity = self.PositionMovie.getEntity()
            slot = entity.getMovieSlot(StartPos)

            sprEntityNode = Sprite.getEntityNode()
            slot.addChild(sprEntityNode)
            self.sprites[Sprite] = [StartPos, WinPos]
            pass

        socketData = Data.getSocket()
        for socketName, movieName in socketData.iteritems():
            socket = self.object.getObject(socketName)
            socket.setEnable(True)
            socket.setInteractive(True)

            swapMovie = self.object.getObject(movieName)
            swapMovie.setEnable(False)
            self.sockets[socket] = swapMovie
            pass

        swapData = Data.getSwap()
        for movieName, tuple in swapData.iteritems():
            movie = self.object.getObject(movieName)
            self.swap[movie] = tuple
            pass
        pass

    def _onPreparationDeactivate(self):
        super(RotateAndReflectElement, self)._onPreparationDeactivate()
        pass

    def _onDeactivate(self):
        super(RotateAndReflectElement, self)._onDeactivate()
        if TaskManager.existTaskChain("Swap") is True:
            TaskManager.cancelTaskChain("Swap")
            pass

        if TaskManager.existTaskChain("Rotate") is True:
            TaskManager.cancelTaskChain("Rotate")
            pass

        for sprite in self.sprites:
            entity = sprite.getEntity()
            entityNode = sprite.getEntityNode()
            entity.removeFromParent()
            self.addChild(entityNode)
            pass
        pass

    pass
