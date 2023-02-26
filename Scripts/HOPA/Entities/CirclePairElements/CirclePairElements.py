from Foundation.DefaultManager import DefaultManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.CirclePairElementsManager import CirclePairElementsManager

from GameField import GameField
from Symbol import Symbol

Enigma = Mengine.importEntity("Enigma")

class CirclePairElements(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "SaveNames")
        Type.addAction(Type, "SaveCircles")
        pass

    def __init__(self):
        super(CirclePairElements, self).__init__()
        self.symbolBySocket = {}
        self.bufferSymbol = None
        self.garbageList = []
        self.delayForShowing = None
        self.cancelTiming = None
        self.Save = []
        pass

    def _onActivate(self):
        super(CirclePairElements, self)._onActivate()
        self.delayForShowing = DefaultManager.getDefaultInt("CirclePairElements", 3)
        self.delayForShowing *= 1000  # speed fix
        self.cancelTiming = DefaultManager.getDefaultInt("CirclePairCancelTiming", 1)
        self.cancelTiming *= 1000  # speed fix

        self.Save = self.SaveNames
        self.prepareGameField()
        pass

    def _stopEnigma(self):
        super(CirclePairElements, self)._stopEnigma()

        self.makeSave()
        self.clearance()
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
        if TaskManager.existTaskChain("CircleRotate"):
            TaskManager.cancelTaskChain("CircleRotate")
        pass

    def makeSave(self):
        for values in self.symbolBySocket.values():
            if values.blocked is False:
                continue
                pass
            self.Save.append(values.name)
        self.object.setParam("SaveNames", self.Save)
        self.object.setParam("SaveCircles", self.GameField.makeSave())
        pass

    def clearance(self):
        for object in self.garbageList:
            if object is None:
                continue
                pass
            object.removeFromParent()
            pass

        self.symbolBySocket = {}
        self.bufferSymbol = None
        self.garbageList = []
        self.delayForShowing = None
        self.cancelTiming = None
        self.Save = []
        pass

    def _onDeactivate(self):
        super(CirclePairElements, self)._onDeactivate()

        self.clearance()
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        if TaskManager.existTaskChain("CircleRotate"):
            TaskManager.cancelTaskChain("CircleRotate")
            pass
        pass

    def _playEnigma(self):
        def __onSocketEnter(socket):
            if self.GameField.isRotate is True:
                return False
                pass
            Symbol = self.symbolBySocket.get(socket)
            if Symbol is None:
                return False
                pass
            Symbol.mouseOn()
            return False
            pass

        def __onSocketLeave(socket):
            if self.GameField.isRotate is True:
                return False
                pass
            Symbol = self.symbolBySocket.get(socket)
            if Symbol is None:
                return False
                pass
            if Symbol.isOpen is True:
                return False
                pass
            Symbol.mouseOff()
            return False
            pass

        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Repeat=True) as tc:
            with tc.addParallelTask(2) as (tc_click, tc_over):
                tc_click.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.__onSocketClick)

                with tc_over.addRaceTask(2) as (tc_over1, tc_over2):
                    tc_over1.addTask("TaskListener", ID=Notificator.onSocketMouseEnter, Filter=__onSocketEnter)
                    tc_over2.addTask("TaskListener", ID=Notificator.onSocketMouseLeave, Filter=__onSocketLeave)
                pass
            pass

        pass

    def __onSocketClick(self, socket):
        if self.GameField.isRotate is True:
            return False
            pass
        Symbol = self.symbolBySocket.get(socket)
        if Symbol is None:
            return False
            pass
        self.turnManage(Symbol)
        complete = self.__isComplete()
        if complete is True:
            self._complete(None)
            pass
        return False
        pass

    def prepareGameField(self):
        CirclePairElements = CirclePairElementsManager.getCirclePairElements(self.EnigmaName)

        movieNameList = CirclePairElements.getMovieNameList()

        movieActivatelist = CirclePairElements.getMovieActiveList()
        movieCloselist = CirclePairElements.getMovieCloseList()

        positionList = CirclePairElements.getPositionsList()
        fieldMovieNameList = CirclePairElements.getFieldMovieList()

        movieSoundList = CirclePairElements.getMovieSoundList()

        movieRingSound = None
        if self.object.hasObject("Movie_RingMoveSound") is True:
            movieRingSound = self.object.getObject("Movie_RingMoveSound")
            pass
        self.GameField = GameField(movieRingSound)

        for name in fieldMovieNameList:
            fieldPartObject = self.object.getObject(name)
            self.GameField.addMovie(fieldPartObject)
            pass

        for i, movieName in enumerate(movieNameList):
            fieldPartName = positionList[i][0]
            fieldPartObject = self.object.getObject(fieldPartName)

            id = "%s" % positionList[i][1]

            fieldPartEntity = fieldPartObject.getEntity()
            MovieSlot = fieldPartEntity.getMovieSlot(id)

            slotChildList = []
            movieBackplate = self.object.generateObject("Movie_Backplate_" + str(id), "Movie_Backplate")
            slotChildList.append(movieBackplate)

            mouseOverObj = self.object.generateObject("Movie_MouseOver_" + str(id), "Movie_MouseOver")
            slotChildList.append(mouseOverObj)

            socket = self.object.generateObject("Socket_Symbol_" + str(id), "Socket_Symbol")
            socket.setInteractive(True)
            slotChildList.append(socket)

            objMovieOpen = self.object.generateObject(movieName + str(id), movieName)
            slotChildList.append(objMovieOpen)

            objMovieActivate = self.object.generateObject(movieActivatelist[i] + "_" + str(id), movieActivatelist[i])
            slotChildList.append(objMovieActivate)

            objMovieClose = self.object.generateObject(movieCloselist[i] + "_" + str(id), movieCloselist[i])
            slotChildList.append(objMovieClose)

            movieSound = None

            if movieSoundList[i] is not None:
                movieSound = self.object.generateObject(movieSoundList[i] + "_" + str(id), movieSoundList[i])
                slotChildList.append(movieSound)
                pass

            for obj in slotChildList:
                entityNode = obj.getEntityNode()
                MovieSlot.addChild(entityNode)
                pass

            symbol = Symbol()
            symbol.onInitialize(movieName, movieBackplate, mouseOverObj, objMovieOpen, objMovieActivate, objMovieClose, movieSound)

            self.symbolBySocket[socket] = symbol

            self.garbageList.extend([objMovieOpen, movieBackplate, objMovieActivate, objMovieClose, mouseOverObj, movieSound, socket])
            pass

        self.restoreFromSave()
        self.GameField.restore(self.SaveCircles)
        pass

    def restoreFromSave(self):
        for values in self.symbolBySocket.values():
            if values.name in self.Save:
                values.restore()
                pass
            pass
        self.Save = []
        pass

    def __isComplete(self):
        for value in self.symbolBySocket.values():
            if value.isOpen is True:
                continue
            return False
            pass

        return True
        pass

    def _complete(self, isSkip):
        self.setComplete()
        pass

    def turnManage(self, Symbol):
        if Symbol.blocked is True:
            return
            pass

        if self.bufferSymbol is None:
            Symbol.openSymbol()
            self.bufferSymbol = Symbol
            return
            pass

        if Symbol is self.bufferSymbol:
            Symbol.closeSymbol()
            self.bufferSymbol = None
            return
            pass

        Symbol.openSymbol()

        if Symbol.name == self.bufferSymbol.name:
            Symbol.blocked = True
            self.bufferSymbol.blocked = True
            self.bufferSymbol = None
            return
            pass

        with TaskManager.createTaskChain() as tc:
            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addTask("TaskDelay", Time=self.delayForShowing)
                with guard_tc.addParallelTask(2) as (tc_1, tc_2):
                    tc_1.addTask("TaskFunction", Fn=Symbol.closeSymbol)
                    tc_2.addTask("TaskFunction", Fn=self.bufferSymbol.closeSymbol)
                    pass
                guard_tc.addTask("TaskDelay", Time=self.cancelTiming)
                guard_tc.addTask("TaskFunction", Fn=self.GameField.Rotate)
                pass
            pass

        self.bufferSymbol = None
        pass

    pass