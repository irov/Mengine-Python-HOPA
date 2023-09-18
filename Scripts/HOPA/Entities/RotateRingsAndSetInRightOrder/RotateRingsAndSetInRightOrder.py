from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.RotateRingsAndSetInRightOrderManager import RotateRingsAndSetInRightOrderManager


Enigma = Mengine.importEntity("Enigma")


class RotateRingsAndSetInRightOrder(Enigma):
    class Ring(object):
        def __init__(self, id, movie, slotOnBG):
            self.id = id
            self.movie = movie
            self.node = Mengine.createNode("Interender")
            entityNode = self.movie.getEntityNode()
            self.node.addChild(entityNode)
            slotOnBG.addChild(self.node)
            self.flagRotate = 0

        def rotateTo(self, source, toAngle, timeTo):
            self.flagRotate += toAngle
            rotateTo = self.flagRotate
            source.addTask("TaskNodeRotateTo", Node=self.node, Time=timeTo, To=-rotateTo)

        def calculateAngle(self, X, Y):
            def distanceBetweenPoints(A, B):
                first = (A[0] - B[0]) ** 2
                second = (A[1] - B[1]) ** 2
                AB = first + second
                return AB ** 0.5

            O = self.movie.getEntityNode().getWorldPosition()
            OX = distanceBetweenPoints(O, X)
            OY = distanceBetweenPoints(O, Y)
            XY = distanceBetweenPoints(X, Y)
            cosAlpha = ((OX ** 2) + (OY ** 2) - (XY ** 2)) / (2 * OX * OY)
            alpha = Mengine.acosf(cosAlpha)
            return alpha

        def calculateA(self, X, Y):
            O = self.movie.getEntityNode().getWorldPosition()
            # vecXY = Mengine.vec2f(X[0] - Y[0], X[1] - Y[1])
            vecOX = Mengine.vec2f(O[0] - X[0], O[1] - X[1])
            vecOY = Mengine.vec2f(O[0] - Y[0], O[1] - Y[1])
            angle = Mengine.angle_from_v2_v2(vecOX, vecOY)
            return angle
            pass

        def scopeClickDown(self, source):
            if self.movie.getEntityType() is "Movie2":
                source.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="ring", isDown=True)
            else:
                source.addTask("TaskMovieSocketClick", Movie=self.movie, SocketName="ring", isDown=True)

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)

    def __init__(self):
        super(RotateRingsAndSetInRightOrder, self).__init__()
        self.tc = None
        self.param = None
        self.rings = {}
        self.Y = None
        self.activeRing = None
        self.MousePositionProviderID = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(RotateRingsAndSetInRightOrder, self)._onPreparation()

    def _onActivate(self):
        super(RotateRingsAndSetInRightOrder, self)._onActivate()

    def _onDeactivate(self):
        super(RotateRingsAndSetInRightOrder, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _skipEnigmaScope(self, skip_tc):
        skip_tc.addScope(self.complete)

    # ==================================================================================================================

    def _loadParam(self):
        self.param = RotateRingsAndSetInRightOrderManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        self.BG = Group.getObject(self.param.SlotsMovie)


        for (RingID, movieName) in self.param.Rings.iteritems():
            movie = Group.getObject(movieName)
            slot = self.BG.getMovieSlot("slot")
            ring = RotateRingsAndSetInRightOrder.Ring(RingID, movie, slot)
            # slot.addChild(ring.node)
            self.rings[RingID] = ring

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._resolveClick)

    def _resolveClick(self, source):
        ringHolder = Holder()
        for ring, race in source.addRaceTaskList(self.rings.values()):
            race.addScope(ring.scopeClickDown)
            race.addFunction(ringHolder.set, ring)

        def holder_scopeClick(source, holder):
            ring = holder.get()
            source.addScope(self._resolveClickOnSocket, ring)

        source.addScope(holder_scopeClick, ringHolder)
        source.addScope(self.checkWin)

    def _resolveClickOnSocket(self, source, ring):
        self.activeRing = ring
        self.Y = None
        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addFunction(self.createMouseProvider)
            parallel_2.addScope(ring.scopeClickUp)
            parallel_2.addFunction(self.removeMouseProvider)

    def createMouseProvider(self):
        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, None, self.__onMousePositionChange)

    def __onMousePositionChange(self, touchID, position):
        if touchID != 0:
            # allow rotating only with one finger for touchpad devices
            return
        with TaskManager.createTaskChain(Repeat=False) as tc:
            with tc.addParallelTask(2) as (SoundEffect, RotateCircle):
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, "RotateRingsAndSetInRightOrder_RotateCircle")
                RotateCircle.addScope(self.updateCirclePos, position.x, position.y)

    def removeMouseProvider(self):
        Mengine.removeMousePositionProvider(self.MousePositionProviderID)
        self.MousePositionProviderID = None

    def updateCirclePos(self, source, x, y):
        if self.Y is None:
            self.Y = (x, y)
            return
        if self.activeRing is not None:
            AngleTo = self.activeRing.calculateAngle(self.Y, (x, y))
            # AngleTo = self.activeRing.calculateA((x, y), self.Y)
            if self.activeRing.id == 2:
                if y < self.activeRing.movie.getEntityNode().getWorldPosition()[1]:
                    # upper semicircle
                    if x < self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, -AngleTo, 1)

                    elif x > self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, 0.1, 100)
                        source.addScope(self.activeRing.rotateTo, -0.1, 100)

                else:
                    # bottom semicircle
                    if x > self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, -AngleTo, 1)
                    elif x < self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, 0.1, 100)
                        source.addScope(self.activeRing.rotateTo, -0.1, 100)


            else:
                if y < self.activeRing.movie.getEntityNode().getWorldPosition()[1]:
                    # upper semicircle
                    if x > self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, AngleTo, 1)
                    elif x < self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, -0.1, 100)
                        source.addScope(self.activeRing.rotateTo, 0.1, 100)

                else:
                    # bottom semicircle
                    if x < self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, AngleTo, 1)
                    elif x > self.Y[0]:
                        source.addScope(self.activeRing.rotateTo, -0.1, 100)
                        source.addScope(self.activeRing.rotateTo, 0.1, 100)

            self.Y = (x, y)

    def checkWin(self, source):
        ringTemp = None
        for ring in self.rings.values():
            if ringTemp is None:
                ringTemp = ring
                continue
            slotRing = ring.movie.getMovieSlot("checkSlot_{}".format(ringTemp.id))
            slotTempRing = ringTemp.movie.getMovieSlot("checkSlot_{}".format(ring.id))
            slotRingPos = slotRing.getWorldPosition()
            slotTempRingPos = slotTempRing.getWorldPosition()

            if all([
                (slotTempRingPos[0] > slotRingPos[0] - 10),
                (slotTempRingPos[0] < slotRingPos[0] + 10),
                (slotTempRingPos[1] > slotRingPos[1] - 10),
                (slotTempRingPos[1] < slotRingPos[1] + 10)
            ]):
                ringTemp = ring

            else:
                break
        else:
            source.addScope(self.complete)

    def setOnWinPosition(self, source):
        def getRingPos(ring):
            ringPos = ring.movie.getMovieSlot("winPos").getWorldPosition()
            return ringPos

        def getAlphaTo(ring):
            ringPos = getRingPos(ring)
            slotPos = self.BG.getMovieSlot("winPos").getWorldPosition()
            alphaTo = ring.calculateAngle(ringPos, slotPos)
            return alphaTo

        for ring, parallel in source.addParallelTaskList(self.rings.values()):
            with parallel.addIfTask(lambda: getRingPos(ring)[0] < ring.movie.getEntityNode().getWorldPosition()[0]) as (true, false):
                true.addScope(ring.rotateTo, getAlphaTo(ring), 1000)
                false.addScope(ring.rotateTo, -getAlphaTo(ring), 1000)

    def complete(self, source):
        source.addScope(self.setOnWinPosition)
        source.addFunction(self.enigmaComplete)
        source.addFunction(self._cleanUp)

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.param = None

        for ring in self.rings.values():
            if ring.movie.getEnable() is False:
                ring.movie.setEnable(True)
            ring.movie.returnToParent()
            Mengine.destroyNode(ring.node)
        self.rings = {}
