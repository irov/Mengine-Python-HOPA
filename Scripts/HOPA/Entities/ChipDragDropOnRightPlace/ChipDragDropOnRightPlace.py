from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ChipDragDropOnRightPlaceManager import ChipDragDropOnRightPlaceManager
from HOPA.EnigmaManager import EnigmaManager


Enigma = Mengine.importEntity("Enigma")


class ChipDragDropOnRightPlace(Enigma):
    class Chip(object):
        def __init__(self, ChipID, movie, startSlot, finishSlot):
            self.id = ChipID

            self.movie = movie
            if self.movie is None:
                msg = "Enigma ChipDragDropOnRightPlace Chip __init__() Chip with id {} got none Movie arg !!!".format(self.id)
                Trace.log("Entity", 0, msg)
            if not self.movie.isActive():
                msg = "Enigma ChipDragDropOnRightPlace Chip __init__() movie {} parent is not active !!!".format(self.movie.name)
                Trace.log("Entity", 0, msg)

            self.node = movie.getEntityNode()

            self._movie_parent = self.node.getParent()
            if self._movie_parent is None:
                msg = "Enigma ChipDragDropOnRightPlace Chip __init__() movie {} parent is parentless!!!".format(self.movie.name)
                Trace.log("Entity", 0, msg)

            self.startSlot = startSlot
            self.finishSlot = finishSlot
            self.currentPlace = None
            self.selected = False

        def scopeClickDown(self, source):
            source.addTask('TaskMovie2SocketClick', Movie2=self.movie, SocketName='chip', isDown=True)

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)

        def attach(self):
            """
            attach chip to arrow
            :return:
            """
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrowPos = arrow_node.getLocalPosition()

            arrow_node.addChildFront(self.node)

            self.node.setWorldPosition((arrowPos[0], arrowPos[1]))

        def detach(self):
            """
            detach chip from arrow
            :return:
            """
            self.returnToParent()
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrowPos = arrow_node.getLocalPosition()

            entity_node = self.node

            entity_node.setLocalPosition((arrowPos[0], arrowPos[1]))

        def scaleChip(self, source, flag):
            """
            change chip`s size
            :param source:
            :param flag: if flag is True the chip is increasing, if flag is False the chip decreases
            :return: nothing
            """
            scale_time = DefaultManager.getDefaultFloat('ChipDragDropOnRightPlace_ScaleTime', 500)

            scaleTo = (1.0, 1.0, 1.0)
            if flag is True:
                scaleTo = DefaultManager.getDefaultTuple('ChipDragDropOnRightPlace_ScaleTo', (1.2, 1.2, 1.2))

            source.addTask("TaskNodeScaleTo", Node=self.node, To=scaleTo, Time=scale_time)

        def setAlphaChip(self, source, flag):
            """
            change chip`s opacity
            :param source:
            :param flag: if flag is True the chip is appears, if flag is False the chip is disappears
            :return: nothing
            """
            changeAlphaTime = DefaultManager.getDefaultFloat('ChipDragDropOnRightPlace_changeAlphaTime', 500)
            alphaTo = 0.0
            alphaFrom = 0.0
            if flag is True:
                alphaTo = 1.0
            elif flag is False:
                alphaFrom = 1.0
            source.addTask("TaskNodeAlphaTo", Node=self.node, From=alphaFrom, To=alphaTo, Time=changeAlphaTime)

        def moveChipTo(self, source, placeTo):
            def calcP(placeTo, placeFrom):
                if placeTo[0] > placeFrom[0]:
                    return ((placeTo[0] - placeFrom[0]) / 2) + placeFrom[0], placeTo[1] + 100
                elif placeTo[0] < placeFrom[0]:
                    return ((placeFrom[0] - placeTo[0]) / 2) + placeTo[0], placeTo[1] - 100

            point1 = calcP(placeTo, self.node.getLocalPosition())
            moveChipToTime = DefaultManager.getDefaultFloat('ChipDragDropOnRightPlace_moveChipToTime', 1000)

            source.addTask("TaskNodeBezier2To", Node=self.node, Point1=point1, To=placeTo, Time=moveChipToTime)

        def returnToParent(self):
            movie_node = self.movie.getEntityNode()
            if movie_node.getParent() != self._movie_parent:
                self._movie_parent.addChild(movie_node)

            if movie_node.getParent() != self._movie_parent:
                msg = "Enigma ChipDragDropOnRightPlace Chip returnToParent() movie {} parent is invalid!!!".format(self.movie.name)
                Trace.log("Entity", 0, msg)

    def __init__(self):
        super(ChipDragDropOnRightPlace, self).__init__()
        self.tc = None
        self.param = None
        self.BG = None
        self.chips = {}
        self.placedChips = {}
        self.selectedChip = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ChipDragDropOnRightPlace, self)._onPreparation()
        self._loadParam()
        self._setup()

    def _onActivate(self):
        super(ChipDragDropOnRightPlace, self)._onActivate()

    def _onDeactivate(self):
        super(ChipDragDropOnRightPlace, self)._onDeactivate()

    def _onPreparationDeactivate(self):
        super(ChipDragDropOnRightPlace, self)._onPreparationDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._activate()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _skipEnigmaScope(self, source):
        for chip, parallel in source.addParallelTaskList(self.chips.values()):
            parallel.addScope(chip.scaleChip, True)
            parallel.addScope(chip.setAlphaChip, False)
            parallel.addFunction(self.BG.getMovieSlot(self.param.Combs[chip.id][1]).addChild, chip.node)
            parallel.addScope(chip.setAlphaChip, True)
            parallel.addScope(chip.scaleChip, False)

        source.addScope(self.complete, True)

    # ==================================================================================================================

    def _loadParam(self):
        self.param = ChipDragDropOnRightPlaceManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        self.BG = Group.getObject('Movie2_WorkZone')

        chips = {}
        for (ChipID, movieName) in self.param.Chips.iteritems():
            movie = Group.getObject(movieName)
            startSlot = self.BG.getMovieSlot(self.param.Combs[ChipID][0])
            finishSlot = self.BG.getMovieSlot(self.param.Combs[ChipID][1])
            chip = ChipDragDropOnRightPlace.Chip(ChipID, movie, startSlot, finishSlot)
            chips[ChipID] = chip

        self.chips = chips

    def _activate(self):
        for chip in self.chips.itervalues():
            chip.movie.setEnable(True)
            chip.startSlot.addChild(chip.node)

    def _runTaskChain(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._resolveClick)

    def _resolveClick(self, source):
        ringHolder = Holder()
        for chip, race in source.addRaceTaskList(self.chips.values()):
            race.addScope(chip.scopeClickDown)
            race.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipDragDropOnRightPlace_ClickOnChip')
            race.addFunction(ringHolder.set, chip)

        def holder_scopeClick(source, holder):
            chip = holder.get()
            if len(self.placedChips) >= 2 and chip.currentPlace is not None:
                source.addScope(self._selectChip, chip)
            else:
                source.addScope(self._dragDropChip, chip)

        source.addScope(holder_scopeClick, ringHolder)
        source.addScope(self.checkWin)

    def _dragDropChip(self, source, chip):
        with source.addIfTask(lambda: chip.currentPlace is None) as (true, false):
            true.addFunction(chip.attach)
            true.addScope(chip.scopeClickUp)
            true.addFunction(chip.detach)
            true.addFunction(self.checkPlace, chip)

    def setSelected(self, chip, flag):
        chip.selected = flag
        if flag is True:
            self.selectedChip = chip
        elif flag is False:
            self.selectedChip = None

    def _selectChip(self, source, chip):
        if self.selectedChip is None:
            source.addFunction(self.setSelected, chip, True)
            with source.addParallelTask(2) as (SoundEffect, Scale):
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipDragDropOnRightPlace_ScaleChipIncrease'),
                Scale.addScope(chip.scaleChip, True)

        elif self.selectedChip is not None:
            tempChip = self.selectedChip
            with source.addIfTask(lambda: self.selectedChip == chip) as (true, false):
                true.addFunction(self.setSelected, chip, False)
                with true.addParallelTask(2) as (SoundEffect, Scale):
                    SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipDragDropOnRightPlace_ScaleChipDecrease')
                    Scale.addScope(chip.scaleChip, False)

                false.addScope(chip.scaleChip, True)
                with false.addParallelTask(2) as (SoundEffect, Swap):
                    SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipDragDropOnRightPlace_SwapChips')
                    Swap.addScope(self.swapChips, chip)

                with false.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addFunction(self.setSelected, chip, False)
                    parallel_1.addScope(chip.scaleChip, False)

                    parallel_2.addFunction(self.setSelected, tempChip, False)
                    parallel_2.addScope(tempChip.scaleChip, False)

    def swapChips(self, source, chip):
        """
        changes two chips in places
        :param chip:
        :return:
        """

        chip_1 = chip
        chip_2 = self.selectedChip
        slot_chip_1 = self.BG.getMovieSlot('Place_{}'.format(chip_1.currentPlace))
        slot_chip_2 = self.BG.getMovieSlot('Place_{}'.format(chip_2.currentPlace))
        self.object.getEntityNode().addChild(chip_1.node)
        self.object.getEntityNode().addChild(chip_2.node)

        chip_1.node.setWorldPosition(slot_chip_1.getWorldPosition())

        chip_2.node.setWorldPosition(slot_chip_2.getWorldPosition())

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addScope(chip_1.moveChipTo, slot_chip_2.getWorldPosition())
            parallel_1.addFunction(slot_chip_2.addChild, chip_1.node)
            parallel_1.addFunction(chip_1.node.setLocalPosition, (0, 0))

            parallel_2.addScope(chip_2.moveChipTo, slot_chip_1.getWorldPosition())
            parallel_2.addFunction(slot_chip_1.addChild, chip_2.node)
            parallel_2.addFunction(chip_2.node.setLocalPosition, (0, 0))

        chip_1.currentPlace, chip_2.currentPlace = chip_2.currentPlace, chip_1.currentPlace

    def checkPlace(self, chip):
        """
        Checks whether a chip within one of the sockets. If True attaches to the appropriate place, else return to start
        positions
        :param chip:
        :return:
        """
        for i in self.chips:
            socket = self.BG.getSocket('Place_{}'.format(i))
            BoundingBox = Mengine.getHotSpotPolygonBoundingBox(socket)

            minX, maxX, minY, maxY = BoundingBox.minimum.x, BoundingBox.maximum.x, BoundingBox.minimum.y, BoundingBox.maximum.y

            chipPos = chip.node.getLocalPosition()
            if (chipPos[0] > minX) and (chipPos[0] < maxX) and (chipPos[1] > minY) and (chipPos[1] < maxY):
                for placeChip in self.placedChips.values():
                    if placeChip.currentPlace == i:
                        break
                else:
                    slot = self.BG.getMovieSlot('Place_{}'.format(i))
                    slot.addChild(chip.node)
                    chip.node.setLocalPosition((0, 0))
                    chip.currentPlace = i
                    self.placedChips[chip.id] = chip
                    break
        else:
            chip.startSlot.addChild(chip.node)
            chip.node.setLocalPosition((0, 0))

    def checkWin(self, source):
        for chip in self.chips.values():
            if 'Place_{}'.format(chip.currentPlace) != self.param.Combs[chip.id][1]:
                break
        else:
            source.addScope(self.complete)

    def complete(self, source, skip=False):
        source.addTask('TaskMovie2Play', GroupName=EnigmaManager.getEnigmaGroupName(self.EnigmaName),
                       Movie2Name='Movie2_FinalLight', Wait=True)
        if not skip:
            source.addFunction(self.enigmaComplete)

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.param = None

        self.BG = None

        for chip in self.chips.itervalues():
            chip.movie.setEnable(False)
            chip.returnToParent()

        self.chips = {}

        self.placedChips = {}

        self.selectedChip = None
