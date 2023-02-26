from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.DragTheChainToTheRightPlaceManager import DragTheChainToTheRightPlaceManager
from HOPA.EnigmaManager import EnigmaManager

Enigma = Mengine.importEntity("Enigma")

class DragTheChainToTheRightPlace(Enigma):
    class Chip(object):
        def __init__(self, id, movie, slot, chainID):
            self.id = id
            self.movie = movie
            self.node = movie.getEntityNode()
            self.startSlot = slot
            self.slot = slot
            self.chainID = chainID
            self.nextChip = None
            self.previousChip = None

        def changePosition(self, slot):
            self.slot = slot
            # with TaskManager.createTaskChain() as tc:
            #     tc.addTask('TaskNodeMoveTo', Node=self.node, To=self.slot.slot.getWorldPosition(), Time=100)
            self.node.setWorldPosition(self.slot.slot.getWorldPosition())

    class Chain(object):
        def __init__(self, chainID):
            self.ID = chainID
            self.chipList = {}
            self.meshgets = []

    class Slot(object):
        def __init__(self, slotID, slot, socket):
            self.slotID = slotID
            self.slot = slot
            self.socket = socket
            self.chip = None

    class Rope(object):
        def __init__(self, chip1, chip2, meshget):
            self.chips = (chip1, chip2)
            self.meshget = meshget

    def __init__(self):
        super(DragTheChainToTheRightPlace, self).__init__()
        self.tc = None
        self.param = None
        self.BG = None
        self.Graph = {}
        self.Chips = []
        self.Chains = {}
        self.slots = {}
        self.isDownClick = False
        self.selectedSlot = None
        self._affector = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(DragTheChainToTheRightPlace, self)._onPreparation()

    def _onActivate(self):
        super(DragTheChainToTheRightPlace, self)._onActivate()

    def _onDeactivate(self):
        super(DragTheChainToTheRightPlace, self)._onDeactivate()
        self._cleanUp()
    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        for chip in self.Chips:
            startSlot = chip.startSlot
            chip.slot.chip = None
            chip.slot = startSlot
            chip.slot.chip = chip
            chip.node.setWorldPosition(startSlot.slot.getWorldPosition())

        for chain in self.Chains.values():
            for rope in chain.meshgets:
                self.changeMeshgetPosition(rope)
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self._runTaskChain()

    # ==================================================================================================================

    def _loadParam(self):
        self.param = DragTheChainToTheRightPlaceManager.getParam(self.EnigmaName)

    def _setup(self):
        def createMeshget(chip1, chip2):
            koef = 3
            # TextureName = 'MeshgetTexture_Chain_GateMG'
            TextureName = self.param.textureName

            MeshgetTexture = Mengine.getResourceReference(TextureName)
            meshget = Mengine.createNode("Meshget")
            surface = Mengine.createSurface("SurfaceImage")
            surface.setResourceImage(MeshgetTexture)
            surface.setMaterialName("Texture_Blend_WW")
            meshget.setSurface(surface)

            size = Mengine.vec2f(128, 64)

            A = chip1.node.getWorldPosition()
            B = chip2.node.getWorldPosition()
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
        self.BG = Group.getObject('Movie2_BG')
        self.Graph = self.param.Graph

        for i in range(1, self.param.NumOfSlots + 1):
            slot = self.BG.getMovieSlot('slot_{}'.format(i))
            socket = self.BG.getSocket('slot_{}'.format(i))
            slot = DragTheChainToTheRightPlace.Slot('slot_{}'.format(i), slot, socket)
            self.slots['slot_{}'.format(i)] = slot

        for (chainID, ChipParam) in self.param.Chips.iteritems():
            for (slotID, chipType) in ChipParam.iteritems():
                id = self.param.chainParam[chainID].index(slotID) + 1
                movieChip = Group.generateObjectUnique('{}In{}'.format(chipType, slotID), chipType, Enable=True, Play=False)

                slot = self.slots[slotID].slot
                # slot.addChild(movieChip.getEntityNode())
                chip = DragTheChainToTheRightPlace.Chip(id, movieChip, self.slots[slotID], chainID)
                entity_node = self.object.getEntityNode()

                entity_node.addChild(chip.node)
                chip.node.setWorldPosition(slot.getWorldPosition())
                self.slots[slotID].chip = chip

                self.Chips.append(chip)

        self.createChain()

        for chip in self.Chips:
            if chip.chainID not in self.Chains:
                chain = DragTheChainToTheRightPlace.Chain(chip.chainID)
                chain.chipList[chip.id] = chip
                # chain.chipList.append(chip)
                self.Chains[chip.chainID] = chain
            elif chip.chainID in self.Chains:
                self.Chains[chip.chainID].chipList[chip.id] = chip

        for chain in self.Chains.values():
            meshgets = []
            for i, chip in chain.chipList.iteritems():
                if i >= len(chain.chipList):
                    break
                meshget = createMeshget(chip, chain.chipList[i + 1])
                rope = DragTheChainToTheRightPlace.Rope(chip, chain.chipList[i + 1], meshget)
                meshgets.append(rope)
            chain.meshgets = meshgets

    def createChain(self):
        for (chainName, order) in self.param.chainParam.iteritems():
            for i in range(len(order)):
                if i < len(order) - 1:
                    self.slots[order[i]].chip.nextChip = self.slots[order[i + 1]].chip
                if i > 0:
                    self.slots[order[i]].chip.previousChip = self.slots[order[i - 1]].chip

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._resolveClick)

    def _resolveClick(self, source):
        availableSlots = []
        for _, slot in self.slots.iteritems():
            if slot.chip is None:
                continue

            if slot.chip.nextChip is None or slot.chip.previousChip is None:
                for graphParam in self.Graph[slot.slotID]:
                    if self.slots[graphParam[0]].chip is None:
                        availableSlots.append(slot)
                        pass

        ClickHolder = Holder()
        for slot, race in source.addRaceTaskList(availableSlots):
            self.isDownClick = True
            race.addTask("TaskMovie2SocketClick", Movie2=self.BG, SocketName=slot.slotID, isDown=True)
            race.addFunction(ClickHolder.set, slot)

        def holder_scopeClick(source, holder):
            slot = holder.get()
            source.addFunction(self.setSelectedSlot, slot)
            source.addTask("TaskMovie2Play", Movie2=slot.chip.movie, Wait=False, Loop=False)
            source.addScope(self.scopeClickOnSlotWithChip)
            source.addTask("TaskMovie2Stop", Movie2=slot.chip.movie)
            source.addFunction(self.setFirstFrameMovie, slot.chip.movie)

        source.addScope(holder_scopeClick, ClickHolder)

    def setSelectedSlot(self, slot):
        self.selectedSlot = slot

    def setFirstFrameMovie(self, movie):
        movie.setLastFrame(False)

    def scopeClickOnSlotWithChip(self, source):
        source.addFunction(self.createAffector)
        with source.addRepeatTask() as (tc_repeat, tc_until):
            tc_repeat.addScope(self.waitMovieSocketEnter)
            tc_repeat.addFunction(self.checkWin)
            tc_until.addTask('TaskMouseButtonClick', isDown=False)
        # source.addFunction(self.setFirstFrameMovie,self.selectedSlot.chip.movie)
        source.addFunction(self.removeAffector)

    def _searchAvailableSlots(self):
        slot = self.selectedSlot
        listWithAvailableSlots = []
        for graphParam in self.Graph[slot.slotID]:
            if self.slots[graphParam[0]].chip is None:
                if graphParam[1] is None:
                    listWithAvailableSlots.append(self.slots[graphParam[0]])
                else:
                    if self.slots[graphParam[1]].chip is None:
                        listWithAvailableSlots.append(self.slots[graphParam[0]])
                    else:
                        if self.slots[graphParam[1]].chip.chainID != slot.chip.chainID:
                            listWithAvailableSlots.append(self.slots[graphParam[0]])
        return listWithAvailableSlots

    def waitMovieSocketEnter(self, source):
        listWithAvailableSlots = self._searchAvailableSlots()
        if not listWithAvailableSlots:
            source.addBlock()
            return

        socketEnter = Holder()
        for availableSlot, race in source.addRaceTaskList(listWithAvailableSlots):
            race.addTask('TaskMovie2SocketEnter', SocketName=availableSlot.slotID, Movie2=self.BG, isMouseEnter=False)
            race.addFunction(socketEnter.set, availableSlot)

        def holder_scopeEnterSocket(source, holder):
            availableSlot = holder.get()

            if availableSlot is not None:
                with source.addParallelTask(2) as (MoveChain, SoundEffect):
                    SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'DragTheChainToTheRightPlace_MoveChain')
                    MoveChain.addFunction(self.moveChain, availableSlot, self.selectedSlot.chip, self.selectedSlot.chip.chainID)
        source.addScope(holder_scopeEnterSocket, socketEnter)

    def moveChain(self, nextSlot, chipSelect, chainID):
        chain = self.Chains[chainID]
        if chipSelect.nextChip is None and chipSelect.previousChip is not None:
            for chip in chain.chipList.values():
                if chip.previousChip is None:
                    chip.slot.chip = None
                    self.sortChipsChain(True, chip, nextSlot)
                else:
                    if chip.nextChip is not None:
                        if chip.slot.chip.slot.slotID == chip.nextChip.slot.slotID:
                            chip.slot.chip = chip.nextChip
                    else:
                        chip.slot.chip = chipSelect
        elif chipSelect.nextChip is not None and chipSelect.previousChip is None:
            for chip in chain.chipList.values():
                if chip.nextChip is None:
                    chip.slot.chip = None
                    self.sortChipsChain(False, chip, nextSlot)
                else:
                    if chip.previousChip is not None:
                        chip.slot.chip = chip.previousChip
                    else:
                        chip.slot.chip = chipSelect

    def sortChipsChain(self, flag, chip, newSlot):
        if flag is True:
            if chip.nextChip is not None:
                chip.changePosition(chip.nextChip.slot)
                chip.nextChip.slot.chip = chip
                self.sortChipsChain(flag, chip.nextChip, newSlot)
            else:
                chip.changePosition(newSlot)
                newSlot.chip = chip
                self.setSelectedSlot(newSlot)

        elif flag is False:
            if chip.previousChip is not None:
                chip.changePosition(chip.previousChip.slot)
                chip.previousChip.slot.chip = chip
                self.sortChipsChain(flag, chip.previousChip, newSlot)
            else:
                chip.changePosition(newSlot)
                newSlot.chip = chip
                self.setSelectedSlot(newSlot)

    def createAffector(self):
        self._affector = Mengine.addAffector(self._mouse_released_affector)

    def _mouse_released_affector(self, dt):
        selectedChip = self.selectedSlot.chip
        chain = self.Chains[selectedChip.chainID]
        for meshget in chain.meshgets:
            self.changeMeshgetPosition(meshget)
        return False

    def changeMeshgetPosition(self, rope):
        koef = 3

        A = rope.chips[0].node.getWorldPosition()
        B = rope.chips[1].node.getWorldPosition()

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

    def removeAffector(self):
        Mengine.removeAffector(self._affector)
        self._affector = None

    def checkWin(self):
        chain = self.Chains[self.param.winComb[0]]
        winSlots = self.param.winComb[1]
        for chip in chain.chipList.values():
            if chip.slot.slotID not in winSlots:
                break
        else:
            self.complete()

    def complete(self):
        for (_, slot) in self.slots.iteritems():
            slot.socket.disable()
        self.enigmaComplete()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.param = None
        self.BG = None
        self.Graph = {}
        for chip in self.Chips:
            chip.node.removeFromParent()
        self.Chips = []

        for chain in self.Chains.values():
            for rope in chain.meshgets:
                rope.meshget.removeFromParent()
        self.Chains = {}
        self.slots = {}
        self.isDownClick = False
        self.selectedSlot = None
        pass