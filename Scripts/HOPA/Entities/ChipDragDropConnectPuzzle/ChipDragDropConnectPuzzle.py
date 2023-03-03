from Foundation.ArrowManager import ArrowManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ChipDragDropConnectPuzzleManager import ChipDragDropConnectPuzzleManager
from HOPA.EnigmaManager import EnigmaManager


Enigma = Mengine.importEntity("Enigma")


class ChipDragDropConnectPuzzle(Enigma):
    class Chip(object):
        def __init__(self, id, movie):
            self.id = id
            self.movie = movie
            self.preAttachPosition = (0, 0)
            pass

        def scopeClickDown(self, source):
            source.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="socket", isDown=True)

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)

        def attach(self):
            arrow = ArrowManager.getArrow()
            arrowPos = arrow.node.getLocalPosition()

            entity_node = self.movie.getEntityNode()
            self.preAttachPosition = entity_node.getLocalPosition()
            arrow.addChildFront(entity_node)

            entity_node_pos = entity_node.getLocalPosition()
            entity_node.setLocalPosition((entity_node_pos[0] - arrowPos[0], entity_node_pos[1] - arrowPos[1]))

        def deattach(self):
            self.movie.returnToParent()
            arrow = ArrowManager.getArrow()
            arrowPos = arrow.node.getLocalPosition()

            entity_node = self.movie.getEntityNode()
            entity_node_pos = entity_node.getLocalPosition()

            entity_node.setLocalPosition((entity_node_pos[0] + arrowPos[0], entity_node_pos[1] + arrowPos[1]))

        def _calculateDistance(self, x1, y1, x2, y2):
            return Mengine.sqrtf((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

        def tryConnect(self, firstSlot, seconSlot):
            firstPos = firstSlot.getWorldPosition()
            secondPos = seconSlot.getWorldPosition()

            distance = self._calculateDistance(firstPos[0], firstPos[1], secondPos[0], secondPos[1])

            if distance > 20:
                return False

            entity_node = self.movie.getEntityNode()
            pos = entity_node.getLocalPosition()

            offset_x = secondPos[0] - firstPos[0]
            offset_y = secondPos[1] - firstPos[1]

            entity_node.setLocalPosition((pos[0] + offset_x, pos[1] + offset_y))
            return True

        def checkBoundingBox(self):
            socket = self.movie.getSocket('socket')
            # BoundingBox_Chip = socket.getBoundingBox()
            BoundingBox_Chip = Mengine.getHotSpotPolygonBoundingBox(socket)

            GroupName = self.movie.getGroupName()
            Group = GroupManager.getGroup(GroupName)
            BG = Group.getObject('Movie2_BG')
            GameArea = BG.getSocket('game_area')
            # BoundingBox_GameArea = GameArea.getBoundingBox()
            BoundingBox_GameArea = Mengine.getHotSpotPolygonBoundingBox(GameArea)

            minX, maxX, minY, maxY = -BoundingBox_GameArea.minimum.x - 70, BoundingBox_GameArea.maximum.x + 70, -BoundingBox_GameArea.minimum.y - 70, BoundingBox_GameArea.maximum.y + 70
            # minX = -90
            # maxX = 1330
            # minY = -90
            # maxY = 670

            if BoundingBox_Chip.minimum.x < minX:
                return False
            elif BoundingBox_Chip.maximum.x > maxX:
                return False
            elif BoundingBox_Chip.minimum.y < minY:
                return False
            elif BoundingBox_Chip.maximum.y > maxY:
                return False
            return True

        def borderAudit(self):
            if self.checkBoundingBox() is False:
                self.returnOnPreAttachPosition()
                return False
            return True

        def returnOnPreAttachPosition(self):
            node = self.movie.getEntityNode()
            node.setLocalPosition(self.preAttachPosition)

    class ChipsGroup(object):
        def __init__(self):
            self.chips = []

        def attach(self):
            for chip in self.chips:
                chip.attach()

        def deattach(self):
            for chip in self.chips:
                chip.deattach()

        def hasChip(self, chip):
            return chip in self.chips

        def addChip(self, chip):
            if chip is None or chip in self.chips:
                return
            self.chips.append(chip)

        def delChip(self, chip):
            if chip in self.chips:
                self.chips.remove(chip)

        def isEmpty(self):
            return not self.chips

        def getChips(self):
            return self.chips

        def borderAudit(self):
            isValid = True
            for chip in self.chips:
                if chip.checkBoundingBox() is False:
                    isValid = False
                    break

            if isValid is False:
                for chip in self.chips:
                    chip.returnOnPreAttachPosition()
            return isValid

    class Way(object):
        def __init__(self, fromChipID, toChipID, fromSlot, toSlot):
            self.fromChipID = fromChipID
            self.toChipID = toChipID
            self.fromSlot = fromSlot
            self.toSlot = toSlot

    class WayFinder(object):
        def __init__(self):
            self.ways = []

        def addWay(self, way):
            if way is None:
                return
            self.ways.append(way)

        def getWaysForChip(self, chip):
            result = []
            for way in self.ways:
                if way.fromChipID == chip.id:
                    result.append(way)
            return result

    def __init__(self):
        super(ChipDragDropConnectPuzzle, self).__init__()
        self.param = None
        self.tc = None
        self.chips = []

        self.completeChipsGroups = []
        self.wayFinder = None

    def _onPreparation(self):
        super(ChipDragDropConnectPuzzle, self)._onPreparation()
        self.loadParam()
        self.setup()

    def _onActivate(self):
        super(ChipDragDropConnectPuzzle, self)._onActivate()

    def _onDeactivate(self):
        super(ChipDragDropConnectPuzzle, self)._onDeactivate()
        self._cleanUp()

    def _playEnigma(self):
        super(ChipDragDropConnectPuzzle, self)._playEnigma()
        self._runTaskChain()

    def _restoreEnigma(self):
        super(ChipDragDropConnectPuzzle, self)._restoreEnigma()
        self._playEnigma()

    def onEnigmaReset(self):
        self._resetEnigma()

    def _resetEnigma(self):
        # print '-----Reset Enigma------'
        self.resetStartPosition()
        self._cleanUp()
        self.loadParam()
        self.setup()
        self._playEnigma()

    def resetStartPosition(self):
        for chip in self.chips:
            node = chip.movie.getEntityNode()
            node.setLocalPosition((0, 0))

    def loadParam(self):
        self.param = ChipDragDropConnectPuzzleManager.getParam(self.EnigmaName)

    def setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        for (ChipID, MovieName) in self.param.chipsDict.iteritems():
            Movie = Group.getObject(MovieName)
            chip = ChipDragDropConnectPuzzle.Chip(ChipID, Movie)

            self.chips.append(chip)

        self.wayFinder = ChipDragDropConnectPuzzle.WayFinder()

        for path in self.param.graphDict:
            FromChipID, ToChipID = path
            FromConnectionSlotName, ToConnectionSlotName = self.param.graphDict[path]

            FromChip = self.getChipByID(FromChipID)
            ToChip = self.getChipByID(ToChipID)

            FromConnectionSlot = FromChip.movie.getMovieSlot(FromConnectionSlotName)
            ToConnectionSlot = ToChip.movie.getMovieSlot(ToConnectionSlotName)

            way = ChipDragDropConnectPuzzle.Way(FromChipID, ToChipID, FromConnectionSlot, ToConnectionSlot)

            self.wayFinder.addWay(way)

    def _runTaskChain(self):
        ClickHolder = Holder()

        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            for chip, tc_race in tc.addRaceTaskList(self.chips):
                tc_race.addScope(chip.scopeClickDown)
                tc_race.addNotify(Notificator.onSoundEffectOnObject, self.object,
                                  "ChipDragDropConnectPuzzle_AttachChipToArrow")
                tc_race.addFunction(ClickHolder.set, chip)

            tc.addScope(self._resolveClickScope, ClickHolder)
            tc.addFunction(self._checkComplete)

    def getChipByID(self, chipID):
        for chip in self.chips:
            if chip.id == chipID:
                return chip
        return None

    def _tryConnectGroups(self, source, chip):
        chipsGroup = self._getChipGroupByChip(chip)
        for mchip in chipsGroup.getChips():
            ways = self.wayFinder.getWaysForChip(mchip)
            for way in ways:
                fromChip = self.getChipByID(way.fromChipID)
                toChip = self.getChipByID(way.toChipID)

                if fromChip.tryConnect(way.fromSlot, way.toSlot) is False:
                    continue
                toChipGroup = self._getChipGroupByChip(toChip)

                if toChipGroup is not None and chipsGroup is not toChipGroup:
                    [chipsGroup.addChip(Chip) for Chip in toChipGroup.chips]
                    self.completeChipsGroups.remove(toChipGroup)
                    continue
                chipsGroup.addChip(toChip)
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChipDragDropConnectPuzzle_ConnectChips")

        return

    def _tryConnect(self, source, chip):
        ways = self.wayFinder.getWaysForChip(chip)

        for way in ways:
            fromChip = self.getChipByID(way.fromChipID)
            toChip = self.getChipByID(way.toChipID)
            chipsGroup = self._getChipGroupByChip(toChip)
            if chipsGroup is not None:
                if chipsGroup.isEmpty() is False and chipsGroup.hasChip(toChip) is False:
                    continue

            if fromChip.tryConnect(way.fromSlot, way.toSlot) is False:
                continue
            if chipsGroup is None:
                self.completeChipsGroups.append(ChipDragDropConnectPuzzle.ChipsGroup())
                chipsGroup = self.completeChipsGroups[-1]

            if chipsGroup.isEmpty() is True:
                chipsGroup.addChip(toChip)

            chipsGroup.addChip(fromChip)
            source.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChipDragDropConnectPuzzle_ConnectChips")
            return

        return

    def _getChipGroupByChip(self, chip):
        for chipsGroup in self.completeChipsGroups:
            if chipsGroup.hasChip(chip):
                return chipsGroup
        return None

    def _resolveClickScope(self, source, clickHolder):
        chip = clickHolder.get()
        chipGroup = self._getChipGroupByChip(chip)

        if chipGroup is not None:
            source.addFunction(chipGroup.attach)
            source.addScope(chip.scopeClickUp)
            source.addFunction(chipGroup.deattach)
            with source.addIfTask(lambda: chipGroup.borderAudit()) as (source_true, source_false):
                source_false.addTask('AliasMindPlay', MindID='ID_MIND_FAIL01')
            source.addScope(self._tryConnectGroups, chip)
        else:
            source.addFunction(chip.attach)
            source.addScope(chip.scopeClickUp)
            source.addFunction(chip.deattach)
            with source.addIfTask(lambda chip: chip.borderAudit(), chip) as (source_true, source_false):
                source_false.addTask('AliasMindPlay', MindID='ID_MIND_FAIL01')
            source.addScope(self._tryConnect, chip)

    def _checkComplete(self):
        if len(self.completeChipsGroups) != 0:
            completeGroup = self.completeChipsGroups[0].getChips()
            if len(completeGroup) == len(self.chips):
                for chip in self.chips:
                    if self.completeChipsGroups[0].hasChip(chip) is False:
                        return
                self.enigmaComplete()
                self._cleanUp()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.param = None
        self.chips = []
        self.completeChipsGroups = []
