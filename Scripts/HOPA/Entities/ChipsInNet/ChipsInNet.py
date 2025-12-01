from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ChipsInNetManager import ChipsInNetManager
from HOPA.EnigmaManager import EnigmaManager


Enigma = Mengine.importEntity("Enigma")


class ChipsInNet(Enigma):
    class Chip(object):
        def __init__(self, id, movie, startSlot):
            self.id = id
            self.movie = movie
            self.node = movie.getEntityNode()
            self.startSlot = startSlot
            self.attachedChips = []
            self.preAttachPosition = None

        def scopeClickDown(self, source):
            source.addTask('TaskMovie2SocketClick', Movie2=self.movie, SocketName='chip', isDown=True)

        def scopeClickUp(self, source):
            source.addTask('TaskMouseButtonClick', isDown=False)

        def attach(self):
            """
            attach chip to arrow
            :return:
            """
            self.node.removeFromParent()
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrowPos = arrow_node.getLocalPosition()

            arrow_node.addChildFront(self.node)

            self.node.setWorldPosition((arrowPos.x, arrowPos.y))
            self.preAttachPosition = arrowPos

        def detach(self):
            """
            detach chip from arrow
            :return:
            """
            self.movie.returnToParent()
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrowPos = arrow_node.getLocalPosition()

            entity_node = self.node

            entity_node.setLocalPosition((arrowPos[0], arrowPos[1]))

        def move(self, source, to):
            MoveTime = DefaultManager.getDefaultFloat('ChipsInNet_MoveTime', 500)
            source.addTask('TaskNodeMoveTo', Node=self.node, To=to, Time=MoveTime)

    class Rope(object):
        def __init__(self, chip1, chip2, meshget, flag):
            self.chips = (chip1, chip2)
            self.meshget = meshget
            self.IntersectionFlag = flag

    def __init__(self):
        super(ChipsInNet, self).__init__()
        self.tc = None
        self.tc_Rrestore = None
        self.param = None
        self.chips = {}
        self.ropes = []
        self.chipOnCursor = None
        self.MousePositionProviderID = None
        self.countToUpdateRopes = 0
        self._affector = None
        self.Rope = 'MeshgetTexture_Rope_Tile'
        self.SelectedRope = 'MeshgetTexture_Rope_Tile_Select'

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ChipsInNet, self)._onPreparation()
        # print '_onPreparation'

        self._loadParam()
        self._setup()  # self.createAffector()

    def _onActivate(self):
        super(ChipsInNet, self)._onActivate()

        self.__SetupPos()

    def __SetupPos(self):
        pass

    def _onPreparationDeactivate(self):
        super(ChipsInNet, self)._onPreparationDeactivate()
        self._cleanUp()

    def _onDeactivate(self):
        super(ChipsInNet, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction('finishFlag')

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._runTaskChain()

    def _restoreEnigma(self):
        ZoomOpeenDelay = 10.0
        enigmaObject = EnigmaManager.getEnigma(self.EnigmaName)
        self.tc_Rrestore = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Rrestore as tc:
            tc.addDelay(ZoomOpeenDelay)
            tc.addFunction(self.Setup_Ropes)

            if enigmaObject.ZoomFrameGroup is not None:
                tc.addListener(Notificator.onZoomEnter)
                tc.addScope(self.checkLineIntersection)
            tc.addFunction(self._playEnigma)

    def _skipEnigmaScope(self, source):
        source.addScope(self.Scope_complete)
        pass

    def _resetEnigma(self):
        pass

    def _loadParam(self):
        self.param = ChipsInNetManager.getParam(self.EnigmaName)

    def _setup(self):
        def createMeshget(chip1, chip2):
            koef = 4
            TextureName = self.SelectedRope

            MeshgetTexture = Mengine.getResourceReference(TextureName)
            meshget = Mengine.createNode("Meshget")
            surface = Mengine.createSurface("SurfaceImage")
            surface.setResourceImage(MeshgetTexture)
            surface.setMaterialName("Texture_Blend_WW")
            meshget.setSurface(surface)

            size = Mengine.vec2f(128, 64)

            A = chip1.node.getLocalPosition()
            B = chip2.node.getLocalPosition()
            vec = (B.x - A.x, B.y - A.y)
            vecLength = Mengine.length_v2(vec)
            normVec = Mengine.norm_v2(vec)
            vecPerp = Mengine.perp_v2(normVec)
            p1 = A + vecPerp * koef
            p2 = B + vecPerp * koef
            p3 = B - vecPerp * koef
            p4 = A - vecPerp * koef

            positions = [Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p2.x, p2.y, 0), Mengine.vec3f(p3.x, p3.y, 0),

                Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p3.x, p3.y, 0), Mengine.vec3f(p4.x, p4.y, 0), ]
            lineLength = vecLength / 32

            uv = [Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 0), Mengine.vec2f(lineLength, 1),

                Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 1), Mengine.vec2f(0, 1), ]
            self.colors = [Mengine.vec4f(1, 1, 1, 1)] * len(positions)
            self.indices = range(len(positions))
            meshget.setVertices(positions, uv, self.colors, self.indices)
            entity_node = self.object.getEntityNode()
            entity_node.addChildFront(meshget)
            return meshget

        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        self.BG = Group.getObject('Movie2_Environment_Over')
        self.Border = Group.getObject('Movie2_Border')

        for (ChipID, MovieName) in self.param.Chips.iteritems():
            movie = Group.getObject(MovieName)
            slot = self.BG.getMovieSlot('chip_{}'.format(ChipID))
            if self.object.getParam('finishFlag') is True:
                slot = self.BG.getMovieSlot('finishChip_{}'.format(ChipID))
            chip = ChipsInNet.Chip(ChipID, movie, slot)
            slot.addChild(chip.node)
            self.chips[ChipID] = chip

        for chip in self.chips.values():
            attachedChips = []
            for attachedChipID in self.param.Graph[chip.id]:
                attachedChips.append(self.chips[attachedChipID])
            chip.attachedChips = attachedChips

        for chip in self.chips.values():
            listAttachedChips = chip.attachedChips
            for attachedChip in listAttachedChips:
                flag = True
                for rope in self.ropes:
                    if chip in rope.chips and attachedChip in rope.chips:
                        flag = False
                        break
                if flag is False:
                    continue
                meshget = createMeshget(chip, attachedChip)
                rope = ChipsInNet.Rope(chip, attachedChip, meshget, False)
                self.ropes.append(rope)

        with TaskManager.createTaskChain() as tc:
            tc.addScope(self.checkLineIntersection)
        for rope in self.ropes:
            self.changeMeshgetPosition(rope)

    def _runTaskChain(self):
        for chip in self.chips.values():
            chip.node.removeFromParent()
            self.object.getEntityNode().addChild(chip.node)
            chip.node.setWorldPosition(chip.startSlot.getWorldPosition())
        for rope in self.ropes:
            self.changeMeshgetPosition(rope)

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._clickOnChip)

    def _clickOnChip(self, source):
        ClickHolder = Holder()

        for chip, race in source.addRaceTaskList(self.chips.values()):
            race.addScope(chip.scopeClickDown)
            race.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipsInNet_ClickDown')

            race.addFunction(ClickHolder.set, chip)

        def holder_scopeClick(source, holder):
            chip = holder.get()
            if self.object.getParam('finishFlag') is False:
                source.addScope(self._resolveClickOnChip, chip)

        source.addScope(holder_scopeClick, ClickHolder)

    def _resolveClickOnChip(self, source, chip):
        source.addFunction(self.setChipOnCursor, chip)
        source.addFunction(chip.attach)
        source.addFunction(self.createMouseProvider)
        source.addScope(chip.scopeClickUp)
        source.addScope(self.checkLineIntersection)
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipsInNet_ClickUp')

        source.addFunction(self.removeMouseProvider)
        source.addFunction(chip.detach)
        with source.addIfTask(self.checkBorders) as (_, false):
            false.addScope(self.returnChipToPlayArea)
        source.addFunction(self.setChipOnCursor, None)
        source.addScope(self.checkWin)

    def setChipOnCursor(self, chip):
        self.chipOnCursor = chip

    def createMouseProvider(self):
        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, None, self.__onMousePositionChange)

    def removeMouseProvider(self):
        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
            self.MousePositionProviderID = None

    def createAffector(self):
        self._affector = Mengine.addAffector(self._mouse_released_affector)

    def _mouse_released_affector(self, dt):
        for rope in self.ropes:
            self.changeMeshgetPosition(rope)
        # self.checkLineIntersection()
        return False

    def removeAffector(self):
        if self._affector is not None:
            Mengine.removeAffector(self._affector)
            self._affector = None

    def __onMousePositionChange(self, touchID, position):
        self.countToUpdateRopes += 1
        if self.countToUpdateRopes > 10:
            self.updateRopes()
            self.countToUpdateRopes = 0

        for rope in self.ropes:
            self.changeMeshgetPosition(rope)

    def updateRopes(self):
        with TaskManager.createTaskChain() as tc:
            tc.addScope(self.checkLineIntersection)

    def getCorrectRope(self, chip_1, chip_2):
        for rope in self.ropes:
            chips = rope.chips
            if chip_1 in chips and chip_2 in chips:
                return rope

    def Setup_Ropes(self):
        for rope in self.ropes:
            koef = 4
            if rope.IntersectionFlag is True:
                koef = 2

            # A = rope.chips[0].node.getWorldPosition()
            # B = rope.chips[1].node.getWorldPosition()

            A = rope.chips[0].node.getLocalPosition()
            B = rope.chips[1].node.getLocalPosition()

            vec = (B.x - A.x, B.y - A.y)
            vecLength = Mengine.length_v2(vec)
            normVec = Mengine.norm_v2(vec)
            vecPerp = Mengine.perp_v2(normVec)
            p1 = A + vecPerp * koef
            p2 = B + vecPerp * koef
            p3 = B - vecPerp * koef
            p4 = A - vecPerp * koef

            positions = [Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p2.x, p2.y, 0), Mengine.vec3f(p3.x, p3.y, 0),

                Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p3.x, p3.y, 0), Mengine.vec3f(p4.x, p4.y, 0), ]
            lineLength = vecLength / 32

            uv = [Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 0), Mengine.vec2f(lineLength, 1),

                Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 1), Mengine.vec2f(0, 1), ]

            rope.meshget.setVertices(positions, uv, self.colors, self.indices)

    def checkLineIntersection(self, source):
        for rope in self.ropes:
            rope.IntersectionFlag = False

        def checkLine(rope_1, rope_2):
            if rope_1 == rope_2:
                return
            if rope_1.chips[0] in rope_2.chips or rope_1.chips[1] in rope_2.chips:
                return
            P1 = rope_1.chips[0].node.getWorldPosition()
            P2 = rope_1.chips[1].node.getWorldPosition()
            P3 = rope_2.chips[0].node.getWorldPosition()
            P4 = rope_2.chips[1].node.getWorldPosition()

            # P1 = rope_1.chips[0].node.getLocalPosition()
            # P2 = rope_1.chips[1].node.getLocalPosition()
            # P3 = rope_2.chips[0].node.getLocalPosition()
            # P4 = rope_2.chips[1].node.getLocalPosition()
            '''
                equation of line in normal form is Ax + By + C = 0
            '''
            A1 = P1.y - P2.y
            B1 = P2.x - P1.x
            C1 = P1.x * P2.y - P2.x * P1.y

            A2 = P3.y - P4.y
            B2 = P4.x - P3.x
            C2 = P3.x * P4.y - P4.x * P3.y

            '''
                solve the system of equations:
                    ax + by = c
                    dx + ey = f
            '''
            a = A1
            b = B1
            c = -C1

            d = A2
            e = B2
            f = -C2
            try:
                y = (f - (d * c) / a) / (e - (d * b) / a)
                x = (c / a) - ((b * y) / a)
            except ZeroDivisionError:
                y = 0
                x = 0
            # check the membership of the point of the segments
            firstSegmentAlongX = any([
                all([P2.x > P1.x, P1.x <= x, P2.x >= x]),
                all([P2.x < P1.x, P2.x <= x, P1.x >= x])]
            )

            secondSegmentAlongX = any([
                all([P3.x > P4.x, P4.x <= x, P3.x >= x]),
                all([P3.x < P4.x, P3.x <= x, P4.x >= x])]
            )

            firstSegmentAlongY = any([
                all([P2.y > P1.y, P1.y <= y, P2.y >= y]),
                all([P2.y < P1.y, P2.y <= y, P1.y >= y])]
            )

            secondSegmentAlongY = any([
                all([P3.y > P4.y, P4.y <= y, P3.y >= y]),
                all([P3.y < P4.y, P3.y <= y, P4.y >= y])]
            )

            if any([all([firstSegmentAlongX, secondSegmentAlongX]), all([firstSegmentAlongY, secondSegmentAlongY])]):
                rope_1.IntersectionFlag = True
                rope_2.IntersectionFlag = True
            self.enableMeshget(rope_2)

        for rope_1, tc_rope1 in source.addParallelTaskList(self.ropes):
            for rope_2, tc_rope2 in tc_rope1.addParallelTaskList(self.ropes):
                tc_rope2.addFunction(checkLine, rope_1, rope_2)

            source.addFunction(self.enableMeshget, rope_1)

    def enableMeshget(self, rope):
        TextureName = self.SelectedRope
        if rope.IntersectionFlag is True:
            TextureName = self.Rope

        MeshgetTexture = Mengine.getResourceReference(TextureName)
        surface = Mengine.createSurface("SurfaceImage")
        surface.setResourceImage(MeshgetTexture)
        rope.meshget.setSurface(surface)  # self.changeMeshgetPosition(rope)

    def changeMeshgetPosition(self, rope):
        koef = 4
        if rope.IntersectionFlag is True:
            koef = 2

        A = rope.chips[0].node.getWorldPosition()
        B = rope.chips[1].node.getWorldPosition()

        # A = rope.chips[0].node.getLocalPosition()
        # B = rope.chips[1].node.getLocalPosition()

        vec = (B.x - A.x, B.y - A.y)
        vecLength = Mengine.length_v2(vec)
        normVec = Mengine.norm_v2(vec)
        vecPerp = Mengine.perp_v2(normVec)
        p1 = A + vecPerp * koef
        p2 = B + vecPerp * koef
        p3 = B - vecPerp * koef
        p4 = A - vecPerp * koef

        positions = [Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p2.x, p2.y, 0), Mengine.vec3f(p3.x, p3.y, 0),

            Mengine.vec3f(p1.x, p1.y, 0), Mengine.vec3f(p3.x, p3.y, 0), Mengine.vec3f(p4.x, p4.y, 0), ]
        lineLength = vecLength / 32

        uv = [Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 0), Mengine.vec2f(lineLength, 1),

            Mengine.vec2f(0, 0), Mengine.vec2f(lineLength, 1), Mengine.vec2f(0, 1), ]

        rope.meshget.setVertices(positions, uv, self.colors, self.indices)

    def checkBorders(self):
        socket = self.Border.getSocket('border')
        # borders = socket.getBoundingBox()
        borders = Mengine.getHotSpotPolygonBoundingBox(socket)

        minX, maxX, minY, maxY = borders.minimum.x, borders.maximum.x, borders.minimum.y, borders.maximum.y

        chipPosition = self.chipOnCursor.node.getWorldPosition()

        if chipPosition.x < minX:
            return False
        elif chipPosition.x > maxX:
            return False
        elif chipPosition.y < minY:
            return False
        elif chipPosition.y > maxY:
            return False
        return True

    def returnChipToPlayArea(self, source):
        chip = self.chipOnCursor
        newPosition = chip.preAttachPosition
        chip.node.setWorldPosition(newPosition)
        source.addScope(self.checkLineIntersection)

    def checkWin(self, source):
        flag = True
        for rope in self.ropes:
            if rope.IntersectionFlag is True:
                flag = False
                break
        if flag is True:
            source.addScope(self.Scope_complete)

    def Scope_complete(self, source):
        source.addFunction(self.createAffector)
        for chip, parallel in source.addParallelTaskList(self.chips.values()):
            parallel.addScope(chip.move, self.BG.getMovieSlot('finishChip_{}'.format(chip.id)).getWorldPosition())
        source.addFunction(self.removeAffector)
        source.addScope(self.checkLineIntersection)
        source.addFunction(self.object.setParam, 'finishFlag', True)
        source.addFunction(self.enigmaComplete)

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        if self.tc_Rrestore is not None:
            self.tc_Rrestore.cancel()
        self.tc = None
        self.tc_Rrestore = None
        self.param = None
        for chip in self.chips.values():
            chip.movie.returnToParent()  # chip.node.removeFromParent()
        self.chips = {}

        for rope in self.ropes:
            # rope.meshget.removeFromParent()
            Mengine.destroyNode(rope.meshget)

        self.ropes = []
        self.chipOnCursor = None
        self.removeMouseProvider()
