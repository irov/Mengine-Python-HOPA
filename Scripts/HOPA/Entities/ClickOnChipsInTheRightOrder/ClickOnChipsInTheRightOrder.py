from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ClickOnChipsInTheRightOrderManager import ClickOnChipsInTheRightOrderManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class ClickOnChipsInTheRightOrder(Enigma):
    class Chip(object):
        def __init__(self, movie):
            self.movie = movie

    def __init__(self):
        super(ClickOnChipsInTheRightOrder, self).__init__()
        self.param = None
        self.chips = {}
        self.slots = {}
        self.winsComb = {}
        self.flagCheckRightOrder = 0
        self.flagComb = 1
        self.falseClick = False
        self.tc_Before = None
        self.tc = None
        self.onZoomLeave = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ClickOnChipsInTheRightOrder, self)._onPreparation()
        if self.object.getParam('finishFlag') is True:
            self.disableSockets()
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        for i in range(1, 4):
            red = Group.getObject('Movie2_Light_red_{}'.format(i))
            red.setEnable(False)

    def _onActivate(self):
        super(ClickOnChipsInTheRightOrder, self)._onActivate()

    def _onDeactivate(self):
        super(ClickOnChipsInTheRightOrder, self)._onDeactivate()

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, 'finishFlag')

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.loadParam()
        self.setup()
        self.disableMovieLight()
        self.tc_Before = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Before as tc:
            tc.addScope(self.playHint)
            tc.addFunction(self._runTaskChain)

    def _restoreEnigma(self):
        self._playEnigma()

    def _stopEnigma(self):
        pass

    # ==================================================================================================================

    # -------------- _onPreparation methods ----------------------------------------------------------------------------
    def loadParam(self):
        self.param = ClickOnChipsInTheRightOrderManager.getParam(self.EnigmaName)

    def disableMovies(self):
        for (_, chip) in self.chips.iteritems():
            chip.movie.setEnable(False)

    def setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        self.onZoomLeave = Notification.addObserver(Notificator.onZoomLeave, self._onZoomLeave)

        def setupObj(dict, objDict):
            for (slotID, movieName) in dict.iteritems():
                movie = Group.getObject(movieName)
                obj = ClickOnChipsInTheRightOrder.Chip(movie)
                objDict[slotID] = obj

        setupObj(self.param.chipDict, self.chips)
        self.disableMovies()
        setupObj(self.param.slotDict, self.slots)
        self.winsComb = self.param.comb

    def disableMovieLight(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        for i in range(1, 4):
            green = Group.getObject('Movie2_Light_green_{}'.format(i))
            red = Group.getObject('Movie2_Light_red_{}'.format(i))
            green.setEnable(False)
            red.setEnable(False)

    # ==================================================================================================================

    # -------------- Task Chain ----------------------------------------------------------------------------------------
    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.scopeClick)
            pass

    def playHint(self, source):
        for id in self.winsComb[self.flagComb]:
            source.addScope(self.playMovie, self.chips[id])

            DelayTime = DefaultManager.getDefaultFloat('ClickOnChipsInTheRightOrderDelayTime', 300)
            # source.addDelay(DelayTime)

    def scopeClick(self, source):
        clickOnSlot = Holder()
        for (slotID, slot), tc_race in source.addRaceTaskList(self.slots.iteritems()):
            tc_race.addTask('TaskMovie2SocketClick', Movie2=slot.movie, SocketName='slot')
            tc_race.addFunction(clickOnSlot.set, slotID)

        def holder_scopeClick(source, holder):
            clickOnSlotID = holder.get()
            source.addScope(self.playMovie, self.chips[clickOnSlotID])
            source.addScope(self.chekcRightOrderClick, clickOnSlotID)

        source.addScope(holder_scopeClick, clickOnSlot)

    def playMovie(self, source, chip):
        source.addFunction(self.changeEnable, chip)
        source.addTask("TaskMovie2Play", Movie2=chip.movie, Wait=True, Loop=False)
        source.addFunction(self.changeEnable, chip)

    def changeEnable(self, chip):
        chip.movie.setEnable(not chip.movie.getEnable())

    def onLight(self, source):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        movieGreen = Group.getObject('Movie2_Light_green_{}'.format(self.flagComb - 1))
        movieGreen.setEnable(True)
        source.addTask("TaskMovie2Play", Movie2=movieGreen, Wait=True, Loop=False)

    def chekcRightOrderClick(self, source, slotID):
        lisComb = self.winsComb[self.flagComb]

        def setFlagCheckRightOrder(value):
            self.flagCheckRightOrder = value

        def setFalseClick(value):
            self.falseClick = value

        def setFlagComb(value):
            self.flagComb = value

        with source.addIfTask(lambda: lisComb[self.flagCheckRightOrder] == slotID) as (source_true, source_false):
            source_true.addFunction(setFlagCheckRightOrder, self.flagCheckRightOrder + 1)
            source_true.addFunction(setFalseClick, True)

            with source_true.addIfTask(lambda: self.flagCheckRightOrder == len(lisComb)) as (source_true_true, source_true_false):
                source_true_true.addFunction(setFlagComb, self.flagComb + 1)
                source_true_true.addScope(self.onLight)
                source_true_true.addFunction(setFlagCheckRightOrder, 0)

                with source_true_true.addIfTask(lambda: self.flagComb > len(self.winsComb)) as (source_true_true_true, source_true_true_false):
                    source_true_true_true.addFunction(self.complete)
                    source_true_true_false.addScope(self.playHint)

            source_false.addFunction(setFlagCheckRightOrder, 0)
            source_false.addFunction(setFalseClick, False)

        def checkCond():
            if self.falseClick is False and self.object.getParam('finishFlag') is False:
                return True
            else:
                return False

        with source.addIfTask(lambda: checkCond()) as (true, false):
            # true.addScope(self.playHint)
            true.addScope(self.failClick)
            true.addFunction(setFalseClick, False)

    def failClick(self, source):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        movieGreen = Group.getObject('Movie2_Light_green_{}'.format(self.flagComb))
        movieGreen.setEnable(False)
        movieRed = Group.getObject('Movie2_Light_red_{}'.format(self.flagComb))
        movieRed.setEnable(True)

        source.addTask("TaskMovie2Play", Movie2=movieRed, Wait=True, Loop=False)

        source.addScope(self.playHint)

    def complete(self):
        self.disableSockets()
        self.object.setParam('finishFlag', True)
        self.enigmaComplete()

    def disableSockets(self):
        for (_, slot) in self.slots.iteritems():
            slot.movie.getSocket('slot').disable()

    # ==================================================================================================================

    # -------------- _cleanUp ------------------------------------------------------------------------------------------
    def _onZoomLeave(self, zoomGroupName):
        self._cleanUp()

        return False
        pass

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.tc_Before is not None:
            self.tc_Before.cancel()
            self.tc_Before = None

        TaskManager.cancelTaskChain('Hint', False)

        self.chips = {}
        self.slots = {}
        self.flagCheckRightOrder = 0
        self.flagComb = 0
        self.falseClick = 0

        self.param = None

    # ==================================================================================================================
