import math

from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ClickOnChipsAndRotateArrowManager import ClickOnChipsAndRotateArrowManager
from HOPA.EnigmaManager import EnigmaManager


Enigma = Mengine.importEntity("Enigma")


class ClickOnChipsAndRotateArrow(Enigma):
    class Chip(object):
        def __init__(self, id, CommonState, FailState, RightState):
            self.chipID = id
            self.commonState = CommonState
            self.failState = FailState
            self.RightState = RightState
            self.active = False

        def activate(self):
            self.active = True
            self.commonState.setEnable(False)
            self.RightState.setEnable(True)

        def deactivate(self):
            self.active = False
            self.RightState.setEnable(False)
            self.commonState.setEnable(True)

    class Arrow(object):
        def __init__(self, movie, numOfChips, onChip):
            self.movie = movie
            self.node = movie.getEntityNode()
            self.onChip = onChip
            self.startChip = onChip
            self.numOfChips = numOfChips
            self.angleTo = (math.pi * 2 / numOfChips)
            self.timeOnChip = 200  # time of passing one chip
            self.rotateAngle = 0

        def setOnchip(self, new_onChip):
            self.onChip = new_onChip

    def __init__(self):
        super(ClickOnChipsAndRotateArrow, self).__init__()
        self.tc = None
        self.param = None
        self.chips = {}
        self.movieSlots = None
        self.arrow = None
        self.nextSymb = 0

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ClickOnChipsAndRotateArrow, self)._onPreparation()

    def _onActivate(self):
        super(ClickOnChipsAndRotateArrow, self)._onActivate()

    def _onDeactivate(self):
        super(ClickOnChipsAndRotateArrow, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _stopEnigma(self):
        self._cleanUp()

    # ==================================================================================================================

    def _loadParam(self):
        self.param = ClickOnChipsAndRotateArrowManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        for (chipID, (CommonState, FailState, RightState)) in self.param.Chips.iteritems():
            movieCommonState = Group.getObject(CommonState)
            movieFailState = Group.getObject(FailState)
            movieRightState = Group.getObject(RightState)
            movieFailState.setEnable(False)
            movieRightState.setEnable(False)
            chip = ClickOnChipsAndRotateArrow.Chip(chipID, movieCommonState, movieFailState, movieRightState)
            self.chips[chipID] = chip

        BG = Group.getObject(self.param.ArrowSlotMovie)
        slot = BG.getMovieSlot('circle')
        for (arrowName, startPosition) in self.param.Arrow.iteritems():
            Arrow = Group.getObject(arrowName)
            self.arrow = ClickOnChipsAndRotateArrow.Arrow(Arrow, len(self.chips), self.chips[startPosition])
            slot.addChild(self.arrow.node)

        self.movieSlots = Group.getObject(self.param.SlotsMovie)

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._scopeClickOnChip)

    def _scopeClickOnChip(self, source):
        clickOnChip = Holder()
        for (chipID, chip), race in source.addRaceTaskList(self.chips.iteritems()):
            if self.movieSlots.getType() is "ObjectMovie2":
                race.addTask("TaskMovie2SocketClick", Movie2=self.movieSlots, SocketName="socket_{}".format(chipID))
            else:
                race.addTask('TaskMovieSocketClick', Movie=self.movieSlots, SocketName='socket_{}'.format(chipID))
            race.addFunction(clickOnChip.set, chip)

        def holder_scopeClick(source, holder):
            clickOnChip = holder.get()
            source.addScope(self._scopeClick, clickOnChip)

        source.addScope(holder_scopeClick, clickOnChip)

    def _failClick(self, source, chip):
        chip.failState.setEnable(False)
        if chip.failState.getType() is "ObjectMovie2":
            source.addTask("TaskMovie2Play", Movie2=chip.failState, Wait=True)
        else:
            source.addTask('TaskMoviePlay', Movie=chip.failState, Wait=True)
        chip.failState.setEnable(True)

    def _scopeClick(self, source, chip):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ClickOnChipsAndRotateArrow_ClickOnChip')
        with source.addIfTask(lambda: chip.chipID is self.param.winsComb[self.nextSymb]) as (true, false):
            true.addScope(self._trueChoice, chip)
            false.addScope(self._falseChoice)
        pass

    def _trueChoice(self, source, chip):
        self.nextSymb += 1
        source.addFunction(chip.activate)

        with source.addParallelTask(2) as (rotateArrowEffect, soundEffect):
            rotateArrowEffect.addScope(self.rotate, chip)
        source.addFunction(self._checkWin)

    def _falseChoice(self, source):
        self.nextSymb = 0
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ClickOnChipsAndRotateArrow_FailClick')

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            for (_, chip), parallel in parallel_1.addParallelTaskList(self.chips.iteritems()):
                parallel.addFunction(chip.deactivate)
                parallel.addScope(self._failClick, chip)
            with parallel_2.addParallelTask(2) as (rotateArrowEffect, soundEffect):
                rotateArrowEffect.addScope(self.rotate, self.arrow.startChip)

    def rotate(self, source, toChip):
        numOfChips = (toChip.chipID - self.arrow.onChip.chipID) % self.arrow.numOfChips

        def setRotateAngle():
            self.arrow.rotateAngle += self.arrow.angleTo

        def rotateOnOnePosition(source):
            rotateAngle = self.arrow.rotateAngle
            source.addTask('TaskNodeRotateTo', Node=self.arrow.node, To=-rotateAngle, Time=self.arrow.timeOnChip)

        with source.addForTask(numOfChips) as (it, sourceFor):
            with sourceFor.addParallelTask(2) as (Rotate, SoundEffect):
                Rotate.addFunction(setRotateAngle)
                Rotate.addScope(rotateOnOnePosition)
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ClickOnChipsAndRotateArrow_Rotate')
        source.addFunction(self.arrow.setOnchip, toChip)

    def _checkWin(self):
        if self.nextSymb == len(self.param.winsComb):
            self._complete()

    def _complete(self):
        self._cleanUp()
        self.enigmaComplete()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
        self.param = None
        if self.arrow is not None:
            self.arrow.node.removeFromParent()
            self.arrow = None
        self.chips = {}
        self.movieSlots = None
        self.nextSymb = 0
