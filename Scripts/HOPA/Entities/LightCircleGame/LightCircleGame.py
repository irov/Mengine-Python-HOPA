from Foundation.TaskManager import TaskManager
import math
from HOPA.LightCircleGameManager import LightCircleGameManager


Enigma = Mengine.importEntity("Enigma")


class LightCircleGame(Enigma):
    class Reflector(object):
        def __init__(self, PlusCount, MinusCount, ReceiveRange, circle_Id, Ref_Id):
            self.PlusCount = PlusCount
            self.MinusCount = MinusCount
            self.ReceiveRange = ReceiveRange

            self.CircleId = circle_Id
            self.ReflectorId = Ref_Id

            self.Movie = None
            self.PlusSlots = []
            self.MinusSlots = []
            self.MoviesRotateTic = 0

            self.IsOn = False

            self.Init()
            pass

        def Init(self):
            pass

        def setRotate(self, Ang):
            self.CurrentRotate = Ang
            self.OnMovie()
            pass

        def setMovie(self, MovieBase):
            self.MoviesRotateTic = MovieBase.getDuration() / 360

            MovieBaseEntity = MovieBase.getEntity()
            id = "Reflector_%d_%d" % (self.CircleId, self.ReflectorId)
            self.Movie = MovieBaseEntity.getSubMovie(id)

            for i in range(self.PlusCount):
                id = "ref_%d_%d_+%d" % (self.CircleId, self.ReflectorId, i)
                slot = self.__getSlot(id, MovieBase)
                if (slot ia None):
                    break
                self.PlusSlots.append(slot)
                pass

            for i in range(self.MinusCount):
                id = "ref_%d_%d_-%d" % (self.CircleId, self.ReflectorId, i)
                slot = self.__getSlot(id, MovieBase)
                if (slot is None):
                    break
                self.MinusSlots.append(slot)
                pass
            pass

        def __getSlot(self, ID, Movie):
            MovieEntity = Movie.getEntity()
            Object = MovieEntity.getMovieSlot(ID)
            return Object
            pass

        def __getAngleSlot(self, slot):
            pos = slot.getLocalPosition()
            deg = LightCircleGame.getDegree(pos, LightCircleGame.Midle_Point)
            deg = LightCircleGame.getDegree360(deg)
            return deg
            pass

        def getPlusSlots(self):
            return self.PlusSlots
            pass

        def TryOn(self, RefOn, UseDiagonal):
            if (self.IsOn is True):
                return self.IsOn
            circleDif = RefOn.CircleId - self.CircleId
            if (math.fabs(circleDif) == 1):
                if UseDiagonal is True:
                    self.__TryOnDiagonal(RefOn)
                else:
                    self.__TryOnAngle(RefOn)
            self.OnMovie()
            return self.IsOn

        def __TryOnDiagonal(self, RefOn):
            plusSlots = RefOn.getPlusSlots()
            for pSlot in plusSlots:
                pPos = pSlot.getWorldPosition()
                for mSlot in self.MinusSlots:
                    Range = self.ReceiveRange
                    mPos = mSlot.getWorldPosition()
                    difX = pPos[0] - mPos[0]
                    difY = pPos[1] - mPos[1]

                    len = math.sqrt(difX * difX + difY * difY)

                    if (len <= Range):
                        # print pPos, " ", mPos
                        # print len1, " ", len2, " ", lenDif, " ", Range, self, " ",RefOn
                        self.IsOn = True

        def __TryOnAngle(self, RefOn):
            plusSlots = RefOn.getPlusSlots()
            for pSlot in plusSlots:
                pPos = pSlot.getWorldPosition()
                for mSlot in self.MinusSlots:
                    Range = self.ReceiveRange
                    mPos = mSlot.getWorldPosition()
                    angP = LightCircleGame.getDegree(pPos, LightCircleGame.Midle_Point)
                    angP = LightCircleGame.getDegree360(angP)
                    angM = LightCircleGame.getDegree(mPos, LightCircleGame.Midle_Point)
                    angM = LightCircleGame.getDegree360(angM)
                    dif = angP - angM
                    dif = math.fabs(dif)
                    if (dif <= Range):
                        self.IsOn = True

        def ResetEnergy(self):
            if (len(self.MinusSlots) == 0):
                self.setOn(True)
                return True
                pass
            else:
                self.setOn(False)
                return False

        def setOn(self, on):
            self.IsOn = on
            self.OnMovie()

        def OnMovie(self):
            if (self.IsOn is True):
                self.Movie.enable()
            else:
                self.Movie.disable()

        def __str__(self):
            str = "c %d, r %d " % (self.CircleId, self.ReflectorId)
            return str

    class Circle(object):
        def __init__(self, CircleId):
            self.CircleId = CircleId
            self.Reflectors = []

            self.CurrentRotate = 0

        def addReflector(self, Reflector):
            self.Reflectors.append(Reflector)

        def setRotate(self, Ang):
            self.CurrentRotate = Ang
            for ref in self.Reflectors:
                ref.setRotate(Ang)

    Slot_Movie = None
    Midle_Point = None

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "CirclesAngle")
        pass

    def __init__(self):
        super(LightCircleGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        ###PreInit
        self.Game = None

        self.UseDiagonal = False
        self.CirclesNumber = 0
        self.CirclesRotatable = 0
        self.ReflectorNumber = 0
        self.ReflectorRange = 0

        self.RotateTic = 1
        ###Init
        self.Movies = []
        self.MoviesRotateTic = []
        self.HotSpots = []
        self.SocketNames = []

        self.Circles = []

        ###Changebl
        self.CircleClickedID = -1
        self.CircleClickedAngle = 0
        self.MouseClickedAngle = 0
        pass

    def _playEnigma(self):
        self.__PreInit()
        self.__Init()
        self.__InitAlias()
        pass

    def _stopEnigma(self):
        for id in range(self.CirclesNumber):
            if (self.CirclesRotatable[id] == 1):
                if TaskManager.existTaskChain("CircleClick_%d" % (id)) is True:
                    TaskManager.cancelTaskChain("CircleClick_%d" % (id))

        if TaskManager.existTaskChain("SetRotateDirection") is True:
            TaskManager.cancelTaskChain("SetRotateDirection")
            pass

        self.ReInitParamentrs()
        pass

    def __Init(self):
        self.__InitMidlPoint()
        self.__InitReflectors()

        for id in range(self.CirclesNumber):
            self.__InitCircleData(id)
            self.__InitReflectorData(id)
            pass

        for id in range(self.CirclesNumber):
            ang = self.CirclesAngle[id]
            self.__setMovieCurrentAng(id, ang)
            pass

        self.__ReEnergyCircles()
        pass

    def __PreInit(self):
        self.Game = LightCircleGameManager.getGame(self.EnigmaName)
        self.UseDiagonal = self.Game.UseDiagonal
        self.CirclesNumber = self.Game.CirclesNumber
        self.CirclesRotatable = self.Game.CirclesRotatable
        self.ReflectorNumber = self.Game.ReflectorNumber
        if self.CirclesAngle is None:
            CirclesStartAngle = self.Game.CirclesStartAngle
            self.object.setParam("CirclesAngle", CirclesStartAngle)
            pass
        pass

    def __InitMidlPoint(self):
        LightCircleGame.Slot_Movie = self.object.getObject("Movie_CirclePoints")
        MovieCirclePointsEntity = LightCircleGame.Slot_Movie.getEntity()
        id = "midlPoint"
        midlObject = MovieCirclePointsEntity.getMovieSlot(id)
        LightCircleGame.Midle_Point = midlObject.getLocalPosition()
        pass

    def __InitReflectors(self):
        for i in range(self.CirclesNumber):
            circle = LightCircleGame.Circle(i)
            self.Circles.append(circle)
            pass

        for CircleId, reflectors in enumerate(self.ReflectorNumber):
            for ReflectId in range(reflectors):
                RefPlusCount = self.Game.getPlus(CircleId, ReflectId)
                RefMinusCount = self.Game.getMinus(CircleId, ReflectId)
                ReflectorMinusRange = self.Game.getReflectorMinusRange(CircleId, ReflectId)

                ref = LightCircleGame.Reflector(RefPlusCount, RefMinusCount, ReflectorMinusRange, CircleId, ReflectId)
                circle = self.Circles[CircleId]
                circle.addReflector(ref)
            pass
        pass

    def __InitCircleData(self, id):
        Movie = self.object.getObject("Movie_Circle%d" % (id))
        Tic = Movie.getDuration() / 360
        self.Movies.append(Movie)
        self.MoviesRotateTic.append(Tic)

        if (self.CirclesRotatable[id] is True):
            MovieEntity = Movie.getEntity()
            socketName = "socket%d" % (id)
            hotspot = self.__getHotSpot(MovieEntity, socketName)

            self.HotSpots.append(hotspot)
            self.SocketNames.append(socketName)
            pass
        pass

    def __InitReflectorData(self, CircleId):
        refNumber = self.ReflectorNumber[CircleId]
        circle = self.Circles[CircleId]
        Movie = self.Movies[CircleId]
        for id in range(refNumber):
            ref = circle.Reflectors[id]
            ref.setMovie(Movie)
            pass
        pass

    def __InitAlias(self):
        for id in range(self.CirclesNumber):
            if (self.CirclesRotatable[id] == 1):
                self.__InitAliasCircle(id)
            pass

        self.__InitAliasMousePos()
        pass

    def __InitAliasCircle(self, id):
        Movie = self.Movies[id]

        def __SetCircle():
            self.CircleClickedID = id
            self.PrevMousePos = Mengine.getCursorPosition()
            pass

        # ------------------------------------------------------
        with TaskManager.createTaskChain(Name="CircleClick_%d" % (id), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=self.SocketNames[id], Movie=Movie, isDown=True)
            tc.addTask("TaskFunction", Fn=__SetCircle)
            tc.addTask("TaskNotify", ID=Notificator.onLightCircleGameCircleClick)
            pass
        pass

    def __InitAliasMousePos(self):
        def __ClickAngle():
            currentMousePos = Mengine.getCursorPosition()
            self.MouseClickedAngle = LightCircleGame.getDegree(currentMousePos, LightCircleGame.Midle_Point)
            self.CircleClickedAngle = self.__getMovieCurrentAng(self.CircleClickedID)
            pass

        def __Rotate():
            currentMousePos = Mengine.getCursorPosition()
            angNow = LightCircleGame.getDegree(currentMousePos, LightCircleGame.Midle_Point)
            angDif = angNow - self.MouseClickedAngle
            ang = angDif + self.CircleClickedAngle
            ang = LightCircleGame.getDegree360(ang)
            self.object.changeParam("CirclesAngle", self.CircleClickedID, ang)
            self.__setMovieCurrentAng(self.CircleClickedID, ang)
            self.__ReEnergyCircles()
            pass

        # ------------------------------------------------------
        with TaskManager.createTaskChain(Name="SetRotateDirection", Repeat=True) as tc:
            tc.addTask("TaskListener", ID=Notificator.onLightCircleGameCircleClick)
            tc.addTask("TaskFunction", Fn=__ClickAngle)
            with tc.addRepeatTask() as (tc_rotate, tc_until):
                tc_rotate.addTask("TaskMouseMoveDistance", Distance=0)
                tc_rotate.addTask("TaskFunction", Fn=__Rotate)

                tc_until.addTask("TaskMouseButtonClick", isDown=False)

                pass
            pass
        pass

    def __ReEnergyCircles(self):
        Active = []
        DeActive = []
        for circle in self.Circles:
            circleRef = circle.Reflectors
            for refClient in circleRef:
                res = refClient.ResetEnergy()
                if (res is True):
                    Active.append(refClient)
                    pass
                else:
                    DeActive.append(refClient)

        changeAc = True
        while (changeAc):
            changeAc = False
            deaAr = DeActive[:]
            for deAc in deaAr:
                for ac in Active:
                    res = deAc.TryOn(ac, self.UseDiagonal)
                    if (res is True):
                        Active.append(deAc)
                        DeActive.remove(deAc)
                        changeAc = True
                        break

        self.__CheckWin(DeActive)
        pass

    def __CheckWin(self, DeActive):
        for deaAr in DeActive:
            circleId = deaAr.CircleId
            reflectorId = deaAr.ReflectorId
            res = self.Game.checkNeedForWin(circleId, reflectorId)
            if (res is True):
                return
            pass
        self.enigmaComplete()
        pass

    @staticmethod
    def getDegree(pos, Midl):
        xDif = pos[0] - Midl[0]
        yDif = pos[1] - Midl[1]
        angRadian = math.atan2(xDif, -yDif)
        angDeg = math.degrees(angRadian)
        return angDeg
        pass

    @staticmethod
    def getDegree360(Deg):
        if (Deg < 0):
            Deg = Deg % 359
            Deg = Deg + 359
            pass

        Deg = Deg % 359
        return Deg
        pass

    def __getMovieCurrentTiming(self, id):
        Movie = self.Movies[id]
        MovieEntity = Movie.getEntity()
        tim = MovieEntity.getTiming()
        return tim
        pass

    def __setMovieCurrentTiming(self, id, tim):
        Movie = self.Movies[id]
        MovieEntity = Movie.getEntity()
        MovieEntity.setTiming(tim)
        pass

    def __getMovieCurrentAng(self, id):
        Movie = self.Movies[id]
        MovieEntity = Movie.getEntity()
        tim = MovieEntity.getTiming()
        ang = tim / self.MoviesRotateTic[id]
        return ang
        pass

    def __setMovieCurrentAng(self, id, ang):
        Movie = self.Movies[id]
        MovieEntity = Movie.getEntity()
        tim = ang * self.MoviesRotateTic[id]
        MovieEntity.setTiming(tim)

        circle = self.Circles[id]
        circle.setRotate(ang)
        pass

    def __getHotSpot(self, MovieEnt, socketName):
        hotspot = MovieEnt.getSocket(socketName)
        return hotspot
        pass
