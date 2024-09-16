from math import fabs

from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.ProgrammatorForFindWayMGManager import ProgrammatorForFindWayMGManager


Enigma = Mengine.importEntity("Enigma")


class ProgrammatorForFindWayMG(Enigma):
    class Chip(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<Chip {}>".format(self.id)

        def __init__(self, id, movie, power, slotChip):
            self.id = id
            self.movie = movie
            self.node = movie.getEntityNode()
            self.place = None
            self.power = power
            self.preAttachPosition = None
            self.StartSlot = slotChip

        def select(self):
            self.movie.delParam('DisableLayers', 'Glow')

        def scopeClickDown(self, source):
            source.addTask('TaskMovie2SocketClick', Movie2=self.movie, SocketName='chip')

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick")

        def setParent(self):
            if self.place is not None:
                if Mengine.hasTouchpad() is True:
                    self.node.setScale((1.0, 1.0, 1.0))
                self.node.removeFromParent()
                self.place.slot.addChild(self.node)

        def attach(self):
            """
            Attach chip to arrow
            :return:
            """
            if Mengine.hasTouchpad() is True:
                self.node.setScale((1.25, 1.25, 1.0))
            else:
                self.preAttachPosition = self.node.getWorldPosition()
                self.node.removeFromParent()
                arrow = Mengine.getArrow()
                arrow_node = arrow.getNode()
                arrowPos = arrow_node.getLocalPosition()

                arrow_node.addChildFront(self.node)

                self.node.setWorldPosition((arrowPos[0], arrowPos[1]))

        def detach(self):
            """
            Detach chip from arrow and return it on start position
            :return:
            """

            if Mengine.hasTouchpad() is True:
                self.node.setScale((1.0, 1.0, 1.0))
            self.node.removeFromParent()
            self.StartSlot.addChild(self.node)

    class Place(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<Place {}>".format(self.id)

        def __init__(self, id, slot, socket):
            self.id = id
            self.slot = slot
            self.socket = socket
            self.chip = None

    class Cell(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<Cell {}>".format(self.id)

        def __init__(self, id, slot):
            self.id = id
            self.slot = slot
            self.isChipMan = None

    class ChipMan(object):
        def __init__(self, movie, place):
            self.movie = movie
            self.node = movie.getEntityNode()
            self.place = place

        def moveTo(self, source, to):
            moveTime = DefaultManager.getDefaultFloat('MoveChipsToKeyPoints_MoveTime', 1000)

            source.addTask('TaskNodeMoveTo', Node=self.node, To=to, Time=moveTime)

    def __init__(self):
        super(ProgrammatorForFindWayMG, self).__init__()
        self.tc = None
        self.param = None
        self.chips = {}
        self.places = {}
        self.cells = {}
        self.PlayMovie = None
        self.chipMan = None
        self.chipOnArrow = None
        self.canPlay = False
        self.PlayNow = False
        self.IsSkip = False
        self.SemaphoreMoveRace = Semaphore(False, "MoveRace")

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ProgrammatorForFindWayMG, self)._onPreparation()

    def _onActivate(self):
        super(ProgrammatorForFindWayMG, self)._onActivate()

    def _onDeactivate(self):
        super(ProgrammatorForFindWayMG, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._cleanUp()
        self._playEnigma()

    def _skipEnigmaScope(self, source):
        self._resetEnigma()
        self.IsSkip = True
        source.addScope(self.Enigma_Skiperrian)

    def Enigma_Skiperrian(self, source):
        for chip in self.chips.values():
            chip.place = self.places[self.param.skipPosition[chip.id]]
            chip.place.chip = chip
            chip.setParent()
        source.addScope(self.resolveClickOnPlay)

    def _resetEnigma(self):
        if self.chipOnArrow is not None:
            self.chipOnArrow.detach()
        self.chipOnArrow = None

        if self.IsSkip is True:
            with TaskManager.createTaskChain() as skip_tc:
                skip_tc.addBlock()
                return
        if TaskManager.existTaskChain('Skip'):
            TaskManager.cancelTaskChain('Skip')

        self.SemaphoreMoveRace.setValue(True)
        with TaskManager.createTaskChain() as skip_tc:
            skip_tc.addScope(self.returnChipManToStartPosition)

    # ==================================================================================================================

    # -------------- Preparation ---------------------------------------------------------------------------------------

    def _loadParam(self):
        self.param = ProgrammatorForFindWayMGManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        self.BG = Group.getObject('Movie2_BG')

        for (ChipID, (movieName, power)) in self.param.Chips.iteritems():
            MovieChip = Group.getObject(movieName)
            MovieChip.setEnable(True)
            MovieChip.appendParam('DisableLayers', 'Glow')
            slotChip = self.BG.getMovieSlot(self.param.PlacesName[0][0].format(ChipID))
            chip = ProgrammatorForFindWayMG.Chip(ChipID, MovieChip, power, slotChip)
            slotChip.addChild(chip.node)

            self.chips[ChipID] = chip

        name, number = self.param.PlacesName[1]
        for i in range(1, number + 1):
            slot = self.BG.getMovieSlot(name.format(i))
            socket = self.BG.getSocket('panelPlace_{}'.format(i))
            place = ProgrammatorForFindWayMG.Place(i, slot, socket)
            self.places[i] = place

        name, number = self.param.PlacesName[2]
        for i in range(number):
            slot = self.BG.getMovieSlot(name.format(i))
            cell = ProgrammatorForFindWayMG.Cell(i, slot)
            self.cells[i] = cell

        ChipManMovie = Group.getObject(self.param.ChipManMovieName)
        self.chipMan = ProgrammatorForFindWayMG.ChipMan(ChipManMovie, self.cells[0])
        self.chipMan.movie.setEnable(True)
        self.chipMan.node.setWorldPosition(self.chipMan.place.slot.getWorldPosition())
        self.PlayMovie = Group.getObject('Movie2_Play')
        self.BG.getMovieSlot('play').addChild(self.PlayMovie.getEntityNode())
        self.PlayMovie.appendParam('DisableLayers', 'Glow')

    # ==================================================================================================================

    # -------------- Run Task Chain ------------------------------------------------------------------------------------

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._clickOnChip)

    def _clickOnChip(self, source):
        ClickHolder = Holder()

        with source.addRaceTask(2) as (race_1, race_2):
            for chip, race in race_1.addRaceTaskList(self.chips.values()):
                race.addScope(chip.scopeClickDown)
                race.addFunction(ClickHolder.set, chip)

            race_2.addTask('TaskMovie2SocketClick', Movie2=self.BG, SocketName='play', isDown=True)

            race_2.addFunction(ClickHolder.set, None)

        def holder_scopeClick(source, holder):
            clickSocket = holder.get()
            if clickSocket is not None:
                self.canPlay = False
                source.addFunction(self.PlayMovie.appendParam, 'DisableLayers', 'Glow')
                source.addScope(self.resolveClickOnChip, clickSocket)
            elif clickSocket is None:
                source.addScope(self.soundEffectClickPlayClickDown)
                if self.canPlay is True:
                    source.addFunction(self.PlayMovie.appendParam, 'DisableLayers', 'Glow')
                    source.addFunction(self.PlayMovie.appendParam, 'DisableLayers', 'Play')
                    source.addTask('TaskMouseButtonClick', isDown=False)
                    source.addScope(self.soundEffectClickPlayClickUp)
                    source.addFunction(self.PlayMovie.delParam, 'DisableLayers', 'Glow')
                    source.addFunction(self.PlayMovie.delParam, 'DisableLayers', 'Play')
                    source.addScope(self.resolveClickOnPlay)
                else:
                    source.addFunction(self.PlayMovie.appendParam, 'DisableLayers', 'GlowScale')
                    source.addFunction(self.PlayMovie.appendParam, 'DisableLayers', 'Play')
                    source.addTask('TaskMouseButtonClick', isDown=False)
                    source.addScope(self.soundEffectClickPlayClickUp)
                    source.addFunction(self.PlayMovie.delParam, 'DisableLayers', 'Play')
                    source.addFunction(self.PlayMovie.delParam, 'DisableLayers', 'GlowScale')

        source.addScope(holder_scopeClick, ClickHolder)

    # ==================================================================================================================

    # -------------- Click on Chip -------------------------------------------------------------------------------------

    def soundEffectClick(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ProgrammatorForFindWayMG_Click')

    def soundEffectSetChipOnPlace(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ProgrammatorForFindWayMG_SetChipOnPlace')

    def soundEffectClickPlayClickUp(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ProgrammatorForFindWayMG_PlayClickUp')

    def soundEffectClickPlayClickDown(self, source):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ProgrammatorForFindWayMG_PlayClickDown')

    def resolveClickOnChip(self, source, chip):
        # source.addTask('TaskMovie2SocketLeave')
        source.addScope(self.soundEffectClick)
        self.chipOnArrow = chip
        source.addFunction(chip.attach)
        self.SemaphoreDone = Semaphore(False, "Done")

        # source.addScope(chip.scopeClickUp)
        source.addScope(self.scopePanelPlace)
        source.addScope(self.soundEffectSetChipOnPlace)
        with source.addIfTask(lambda: self.SemaphoreDone.getValue() is True) as (true, false):
            true.addFunction(self.checkPlayPossibility)
            false.addFunction(self.invalidPanelPlace, chip)

    def scopePanelPlace(self, source):
        with source.addRaceTask(2) as (valid, invalid):
            for (place, source_place) in valid.addRaceTaskList(self.places.values()):
                source_place.addTask("TaskMovie2SocketClick", SocketName="panelPlace_%s" % place.id, Movie2=self.BG)
                source_place.addFunction(self.checkPanelPlace, place)
            invalid.addTask("TaskMouseButtonClick")
            invalid.addDelay(1)

    def invalidPanelPlace(self, chip):
        if chip.place is not None:
            chip.place.chip = None
        chip.place = None
        chip.detach()
        self.chipOnArrow = None

    def checkPanelPlace(self, place):
        """
            If found panel place where is chip, SemaphoreDone set True, else SemaphoreDone set False
        """
        chip = self.chipOnArrow

        # print "[{}]: {}, [{}]: {}".format(chip, chip.place, place, place.chip)

        if place.chip is chip:  # CASE_0 - clicked_place is clicked_chip place -> restore
            # print "CASE 0"

            chip.setParent()

            self.chipOnArrow = None
            self.SemaphoreDone.setValue(True)

        elif place.chip is None:  # CASE_1 - clicked_place is empty -> set clicked_chip to clicked_place
            # print "CASE 1"

            if chip.place is not None:
                chip.place.chip = None

            chip.place = place
            place.chip = chip
            chip.setParent()

            self.chipOnArrow = None
            self.SemaphoreDone.setValue(True)

        else:
            if chip.place is not None:  # CASE_2 - clicked_chip has place clicked_place has chip -> swap
                # print "CASE 2"

                temp_place = chip.place
                temp_chip = place.chip

                chip.place = place
                place.chip = chip
                chip.setParent()

                temp_chip.place = temp_place
                temp_place.chip = temp_chip
                temp_chip.setParent()

                self.chipOnArrow = None
                self.SemaphoreDone.setValue(True)

            else:  # CASE_3 - clicked_chip has no place clicked_place has chip -> clicked_chip to clicked_place, clicked_place old chip - restore
                # print "CASE 3"

                temp_chip = place.chip

                chip.place = place
                place.chip = chip
                chip.setParent()

                temp_chip.place = None
                temp_chip.detach()

                self.chipOnArrow = None
                self.SemaphoreDone.setValue(True)

    def checkPlayPossibility(self):
        flag = True
        for place in self.places.values():
            if place.chip is None:
                flag = False
                break

        self.canPlay = flag
        if flag is True:
            self.PlayMovie.delParam('DisableLayers', 'Glow')

    # ==================================================================================================================

    # -------------- Click on Play Button ------------------------------------------------------------------------------

    def resolveClickOnPlay(self, source):
        source.addFunction(self.setPlayNow, True)
        count = len(self.places)

        tempCell = self.chipMan.place.id
        routList = []
        for place in self.places.values():
            power = place.chip.power
            routList.append(self.getRouteList(tempCell, tempCell + power))
            tempCell = fabs(tempCell + power)

        self.SemaphoreMoveRace = Semaphore(False, "MoveRace")
        with source.addRaceTask(2) as (race_1, race_2):
            if routList[0][0] < 0:
                count = 0
                race_1.addSemaphore(self.SemaphoreMoveRace, To=True)

            with race_1.addForTask(count) as (it, sourceFor):
                sourceFor.addScope(self.moveChipMan, routList, it)
                sourceFor.addFunction(self.checkFailCell)

            race_2.addSemaphore(self.SemaphoreMoveRace, From=True)

        with source.addIfSemaphore(self.SemaphoreMoveRace, True) as (tc_skip, tc_end):
            tc_skip.addScope(self.returnChipManToStartPosition)

            tc_end.addFunction(self.checkWin)

        source.addFunction(self.setPlayNow, False)

    def setPlayNow(self, flag):
        self.PlayNow = flag

    def getRouteList(self, moveFrom, moveTo):
        routeList = []
        routLength = fabs(moveFrom - moveTo)
        if moveTo > moveFrom:
            routeList = [i for i in range(int(moveFrom) + 1, int(moveTo) + 1)]
        else:
            routeList = [i for i in range(int(moveFrom) - 1, int(moveTo) - 1, -1)]
        return routeList

    def moveChipMan(self, source, routList, it):
        self.disableChipsSelect()
        rout = []
        if it is not None:
            rout = routList[it.getValue()]
            ind = it.getValue() + 1
            self.places[ind].chip.select()
        else:
            self.SemaphoreMoveRace.setValue(False)
            rout = routList

        cells_len = len(self.cells) - 1
        count = len(rout)

        if count != 0:
            if rout[-1] >= cells_len > rout[0]:
                count = cells_len - (rout[0] - 1)

        def moveTo(source, it):
            if (rout[it.getValue()] <= len(self.cells) - 1) and (rout[it.getValue()] >= 0):
                self.chipMan.place = self.cells[rout[it.getValue()]]
                to = self.cells[rout[it.getValue()]].slot.getWorldPosition()
                moveTime = DefaultManager.getDefaultFloat('ProgrammatorForFindWayMG_MoveTime', 1000)
                with source.addParallelTask(2) as (move, soundEffect):
                    move.addTask('TaskNodeMoveTo', Node=self.chipMan.node, To=to, Time=moveTime)
                    soundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ProgrammatorForFindWayMG_MoveChipMan')

        def checkRoutInd():
            if (rout[it.getValue()] > len(self.cells) - 1) or (rout[it.getValue()] < 0):
                self.SemaphoreMoveRace.setValue(True)

        with source.addForTask(count) as (it, sourceFor):
            sourceFor.addFunction(checkRoutInd)
            sourceFor.addSemaphore(self.SemaphoreMoveRace, From=False)
            sourceFor.addScope(moveTo, it)

    def checkFailCell(self):
        if self.chipMan.place.id in self.param.FailCells:
            self.SemaphoreMoveRace.setValue(True)

    def returnChipManToStartPosition(self, source):
        self.canPlay = False
        source.addFunction(self.returnChipsToStartPositions)
        source.addFunction(self.disableChipsSelect)
        source.addTask("TaskMovie2Interrupt", Movie2=self.chipMan.movie)

        source.addScope(self.moveChipMan, self.getRouteList(self.chipMan.place.id, 0), None)

    def returnChipsToStartPositions(self):
        for chip in self.chips.values():
            if chip.place is not None:
                chip.place.chip = None
                chip.place = None
            chip.detach()

    def disableChipsSelect(self):
        for chip in self.chips.values():
            chip.movie.appendParam('DisableLayers', 'Glow')

    def checkWin(self):
        if self.chipMan.place.id == self.param.FinishCellID:
            self.complete()

    def complete(self):
        self.enigmaComplete()

    # ==================================================================================================================

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.param = None

        for chip in self.chips.values():
            chip.node.removeFromParent()
            chip.movie.setEnable(False)
        self.chips = {}
        if self.PlayMovie != None:
            self.PlayMovie.getEntityNode().removeFromParent()
            self.PlayMovie = None
        if self.chipMan != None:
            self.chipMan.node.removeFromParent()
            self.chipMan.movie.setEnable(False)
            self.chipMan = None
        self.chipOnArrow = None
        self.canPlay = False
        self.PlayNow = False
