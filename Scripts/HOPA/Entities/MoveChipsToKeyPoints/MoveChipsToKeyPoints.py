from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.MoveChipsToKeyPointsManager import MoveChipsToKeyPointsManager


Enigma = Mengine.importEntity("Enigma")


class MoveChipsToKeyPoints(Enigma):
    class Chip(object):
        def __init__(self, ChipID, MovieChip):
            self.id = ChipID
            self.movie = MovieChip
            self.node = MovieChip.getEntityNode()
            self.slot = None

    class Slot(object):
        def __init__(self, id, SlotName, chip):
            self.id = id
            self.slot = SlotName
            self.chip = chip

    def __init__(self):
        super(MoveChipsToKeyPoints, self).__init__()
        self.tc = None
        self.param = None
        self.BG = None
        self.chips = {}
        self.slots = {}
        self.sockets = []

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(MoveChipsToKeyPoints, self)._onPreparation()

    def _onActivate(self):
        super(MoveChipsToKeyPoints, self)._onActivate()

    def _onDeactivate(self):
        super(MoveChipsToKeyPoints, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _skipEnigmaScope(self, source):
        source.addScope(self.Enigma_Skipperian)

    def Enigma_Skipperian(self, source):
        moveTime = DefaultManager.getDefaultFloat('MoveChipsToKeyPoints_MoveTime', 2000)
        for (ChipID, FinishSlotID), parallel in source.addParallelTaskList(self.param.WinParam.iteritems()):
            tempSlot = self.chips[ChipID].slot
            with parallel.addParallelTask(2) as (p1, p2):
                p1.addFunction(self.beforeNodeMove, self.chips[ChipID])
                # p1.addTask('TaskNodeMoveTo', Node=self.chips[ChipID].node,
                #                  To=self.slots[FinishSlotID].slot.getWorldPosition(),
                #                  Time=moveTime)
                p1.addFunction(self.afterNodeMove, self.chips[ChipID], self.slots[FinishSlotID])

                p2.addFunction(self.beforeNodeMove, self.slots[FinishSlotID].chip)
                # p2.addTask('TaskNodeMoveTo', Node=self.slots[FinishSlotID].chip.node,
                #            To=tempSlot.slot.getWorldPosition(),
                #            Time=moveTime)
                p2.addFunction(self.afterNodeMove, self.slots[FinishSlotID].chip, tempSlot)

        source.addFunction(self.complete)

    def _resetEnigma(self):
        self._cleanUp()
        self._playEnigma()  # moveTime = DefaultManager.getDefaultFloat('MoveChipsToKeyPoints_MoveTime', 2000)  # with TaskManager.createTaskChain(Name='Reset') as reset_tc:  #     '''  #     slotID	SlotName	StartChip  #     '''  #     for (slotID, slotParam), parallel in reset_tc.addParallelTaskList(self.param.Slots.iteritems()):  #         parallel.addFunction(self.beforeNodeMove, self.chips[slotParam[1]])  #         parallel.addTask('TaskNodeMoveTo', Node=self.chips[slotParam[1]].node,  #                          To=self.slots[slotID].slot.getWorldPosition(),  #                          Time=moveTime)  #         parallel.addFunction(self.afterNodeMove, self.chips[slotParam[1]], self.slots[slotID])

    def _restoreEnigma(self):
        self._cleanUp()
        self._playEnigma()

    # ==================================================================================================================

    def _loadParam(self):
        self.param = MoveChipsToKeyPointsManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        self.BG = Group.getObject('Movie_BGforMG')

        for (ChipID, movieName) in self.param.Chips.iteritems():
            MovieChip = Group.getObject(movieName)
            chip = MoveChipsToKeyPoints.Chip(ChipID, MovieChip)
            self.chips[ChipID] = chip

        for (slotID, slotParam) in self.param.Slots.iteritems():
            slotObj = self.BG.getMovieSlot(slotParam[0])
            slotObj.addChild(self.chips[slotParam[1]].node)
            slot = MoveChipsToKeyPoints.Slot(slotID, slotObj, self.chips[slotParam[1]])
            self.chips[slotParam[1]].slot = slot
            self.slots[slotID] = slot

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._resolveClick)

    def _resolveClick(self, source):
        ClickHolder = Holder()

        for i, race in source.addRaceTaskList(range(1, 5)):
            race.addTask('TaskMovieSocketClick', SocketName='socket_{}'.format(i), Movie=self.BG)
            race.addFunction(ClickHolder.set, i)

        def holder_scopeClick(source, holder):
            clickSocket = holder.get()
            with source.addParallelTask(2) as (resolveClick, soundEffect):
                resolveClick.addScope(self._resolveClickOnSocket, clickSocket)
                soundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'MoveChipsToKeyPoints_MoveChips')

        source.addScope(holder_scopeClick, ClickHolder)
        source.addFunction(self.checkWin)

    def beforeNodeMove(self, chip):
        chip.node.removeFromParent()
        self.object.getEntityNode().addChild(chip.node)
        chip.node.setLocalPosition(chip.slot.slot.getWorldPosition())

    def afterNodeMove(self, chip, nextChipSlot):
        chip.node.removeFromParent()
        nextChipSlot.slot.addChild(chip.node)
        chip.node.setLocalPosition((0, 0))
        chip.slot = nextChipSlot
        chip.slot.chip = chip

    def _resolveClickOnSocket(self, source, socketID):
        chip = self.searchChipInSocket(socketID)
        NeighboringChipsList = self.searchNeighboringChips(chip.slot)

        tempSlot = None
        moveTime = DefaultManager.getDefaultFloat('MoveChipsToKeyPoints_MoveTime', 2000)

        for (ind, chip), parallel in source.addParallelTaskList(enumerate(NeighboringChipsList)):
            if ind == 0:
                tempSlot = chip.slot
            parallel.addFunction(self.beforeNodeMove, chip)
            if ind == len(NeighboringChipsList) - 1:
                parallel.addTask('TaskNodeMoveTo', Node=chip.node, To=tempSlot.slot.getWorldPosition(), Time=moveTime)
                parallel.addFunction(self.afterNodeMove, chip, tempSlot)
            else:
                parallel.addTask('TaskNodeMoveTo', Node=chip.node, Time=moveTime,
                                 To=NeighboringChipsList[(ind + 1) % len(NeighboringChipsList)].slot.slot.getWorldPosition())
                parallel.addFunction(self.afterNodeMove, chip,
                                     NeighboringChipsList[(ind + 1) % len(NeighboringChipsList)].slot)

    def searchChipInSocket(self, socketID):
        """
        search chip within this socket
        :param socketID:
        :return: chip within this socket
        """
        socket = self.BG.getSocket('socket_{}'.format(socketID))
        # BoundingBox = socket.getBoundingBox()
        BoundingBox = Mengine.getHotSpotPolygonBoundingBox(socket)
        minX, maxX, minY, maxY = BoundingBox.minimum.x, BoundingBox.maximum.x, BoundingBox.minimum.y, BoundingBox.maximum.y

        for (_, chip) in self.chips.iteritems():
            chipPos = chip.node.getWorldPosition()
            if chipPos[0] > minX and chipPos[0] < maxX and chipPos[1] > minY and chipPos[1] < maxY:
                return chip

    def searchNeighboringChips(self, slot):
        """
        search Neighboring Slot (6 pieces)
        :param slot: slot around which neighbors are located
        :return: Neighboring chips list (arranged clockwise starting with the upper chip)
        """
        upperChipID = slot.id - (len(self.chips) ** 0.5)
        lowerChipID = slot.id + (len(self.chips) ** 0.5)

        NeighboringChips_listOfIndex = [
            upperChipID,
            upperChipID + 1,
            slot.id + 1,
            lowerChipID + 1,
            lowerChipID,
            lowerChipID - 1,
            slot.id - 1,
            upperChipID - 1
        ]

        NeighboringChips_listWithChips = []
        for i in NeighboringChips_listOfIndex:
            NeighboringChips_listWithChips.append(self.slots[i].chip)

        return NeighboringChips_listWithChips

    def checkWin(self):
        flag = True
        for (chipID, slotID) in self.param.WinParam.iteritems():
            if self.chips[chipID].slot.id != slotID:
                flag = False
        if flag is True:
            self.complete()

    def complete(self):
        for i in range(1, 5):
            socket = self.BG.getSocket('socket_{}'.format(i))
            socket.disable()
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.enigmaComplete()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()

        for (_, chip) in self.chips.iteritems():
            # chip.movie.setEnable(False)
            chip.node.removeFromParent()

        self.tc = None
        self.param = None
        self.BG = None
        self.chips = {}
        self.slots = {}
        self.sockets = []
