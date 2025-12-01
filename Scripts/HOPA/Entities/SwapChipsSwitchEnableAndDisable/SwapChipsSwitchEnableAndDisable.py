from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.SwapChipsSwitchEnableAndDisableManager import SwapChipsSwitchEnableAndDisableManager


Enigma = Mengine.importEntity("Enigma")


class SwapChipsSwitchEnableAndDisable(Enigma):
    class Chip(object):
        def __init__(self, slot, slotID, movie, type):
            self.slot = slot
            self.slotID = slotID
            self.movie = movie
            self.type = type
            self.node = self.movie.getEntityNode()
            self.selected = False

    class Slot(object):
        def __init__(self, slotID, movie, slotOnBG):
            self.id = slotID
            self.movie = movie
            self.slot = self.movie.getMovieSlot('slot')
            self.node = Mengine.createNode('Interender')
            entityNode = self.movie.getEntityNode()
            self.node.addChild(entityNode)
            slotOnBG.addChild(self.node)

    def __init__(self):
        super(SwapChipsSwitchEnableAndDisable, self).__init__()
        self.tc = None
        self.param = None
        self.chips = {}
        self.redChips = {}
        self.blueChips = {}
        self.greenChips = {}
        self.blackChips = {}
        self.slots = []

        self.selectedBlueChips = {}
        self.selectedRedChips = {}
        self.selectedGreenChips = {}
        self.selectedBlackChips = {}
        self.isSelectedChipsList = []
        self.visibleChips = []

        self.isSelectedChip = False

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(SwapChipsSwitchEnableAndDisable, self)._onPreparation()

        self.disableNotUsedChips()

    def _onActivate(self):
        super(SwapChipsSwitchEnableAndDisable, self)._onActivate()

        if self.object.getParam('finishFlag') is True:
            visChips = self.object.getVisibleChips()
            self.loadParam()
            self.setup()
            self.setStartComb(visChips)

    def _onDeactivate(self):
        super(SwapChipsSwitchEnableAndDisable, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction('visibleChipsParam')
        Type.addAction('finishFlag')

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.loadParam()
        self.setup()
        self.setStartComb(self.param.startCombDict)
        self.disableNotUsedChips()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    # ==================================================================================================================

    # -------------- _onPreparation methods ----------------------------------------------------------------------------
    def loadParam(self):
        self.param = SwapChipsSwitchEnableAndDisableManager.getParam(self.EnigmaName)

    def setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = self.object
        bg_movie2 = "Movie2_BG_Slots"
        bg_movie1 = "Movie_BG_Slots"

        def searchSlot(slotID):
            for slot in self.slots:
                if slot.id == slotID:
                    return slot

        for (slotID, movieName) in self.param.slotDict.iteritems():
            if Group.hasObject(bg_movie2):
                MovieBG = Group.getObject(bg_movie2)
            elif Group.hasObject(bg_movie1):
                MovieBG = Group.getObject(bg_movie1)
            else:
                Trace.log("Entity", 0,
                          "Not found {!r} or {!r} objects in {!r} group!".format(bg_movie2, bg_movie1, GroupName))
                continue

            slotOnBG = MovieBG.getMovieSlot('slot_{}'.format(slotID))
            Movie = Group.getObject(movieName)
            slot = SwapChipsSwitchEnableAndDisable.Slot(slotID, Movie, slotOnBG)
            self.slots.append(slot)

        def setupChips(dict, chipsList):
            for (slotID, movieName) in dict.iteritems():
                movie = Group.getObject(movieName)
                slot = searchSlot(slotID)
                chip = SwapChipsSwitchEnableAndDisable.Chip(slot, slotID, movie, movieName.split('_')[1])
                chipsList[slotID] = chip

        setupChips(self.param.redDict, self.redChips)
        setupChips(self.param.blueDict, self.blueChips)
        setupChips(self.param.greenDict, self.greenChips)
        setupChips(self.param.blackDict, self.blackChips)
        setupChips(self.param.blueSelectedDict, self.selectedBlueChips)
        setupChips(self.param.redSelectedDict, self.selectedRedChips)
        setupChips(self.param.greenSelectedDict, self.selectedGreenChips)
        setupChips(self.param.blackSelectedDict, self.selectedBlackChips)

        def setupSelectedSlots(dict):
            for (_, light) in dict.iteritems():
                light.slot.slot.addChild(light.node)
                light.movie.setEnable(False)

        setupSelectedSlots(self.selectedBlueChips)
        setupSelectedSlots(self.selectedRedChips)
        setupSelectedSlots(self.selectedGreenChips)
        setupSelectedSlots(self.selectedBlackChips)

    def setStartComb(self, dict):
        for (slotID, type) in dict.iteritems():
            if type == 'Red':
                self.setMoviesOnSlots(self.redChips, slotID)
            elif type == 'Blue':
                self.setMoviesOnSlots(self.blueChips, slotID)
            elif type == 'Green':
                self.setMoviesOnSlots(self.greenChips, slotID)
            elif type == 'Black':
                self.setMoviesOnSlots(self.blackChips, slotID)

    def setMoviesOnSlots(self, chipsList, slotID):
        chip = chipsList[slotID]
        self.setChipInLastFrame(chip, True)
        chip.slot.slot.addChild(chip.node)
        self.visibleChips.append(chip)  # self.object.addChipToVisibleChips(chip)

    def setChipInLastFrame(self, chip, flag):
        with TaskManager.createTaskChain(Name="play") as source:
            source.addTask("TaskMovieLastFrame", Movie=chip.movie, Value=flag)

    # ==================================================================================================================

    # -------------- Task Chain ----------------------------------------------------------------------------------------
    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.scopeClick)

    def scopeClick(self, source):
        clickSlotHolder = Holder()
        for slot, tc_race in source.addRaceTaskList(self.slots):
            movie_type = slot.movie.getType()
            if movie_type == "ObjectMovie2":
                tc_race.addTask("TaskMovie2SocketClick", Movie2=slot.movie, SocketName="slot")
            elif movie_type == "ObjectMovie":
                tc_race.addTask("TaskMovieSocketClick", Movie=slot.movie, SocketName="slot")

            tc_race.addFunction(clickSlotHolder.set, slot)

        def holder_scopeClick(source, holder):
            clickSlot = holder.get()
            source.addScope(self.scopeSelectChip, clickSlot)

        source.addScope(holder_scopeClick, clickSlotHolder)

        source.addFunction(self.checkWin)

    def scopeSelectChip(self, source, slot):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "SwapChipsSwitchEnableAndDisable_SelectChip")
        chip = None

        for searchedChip in self.visibleChips:
            if searchedChip.slot == slot:
                chip = searchedChip

        selectedList = self.getCorrectChipsList(chip.type)[1]

        def chipSelected(flag):
            selectedList[slot.id].movie.setEnable(flag)
            chip.movie.setEnable(not flag)
            chip.selected = flag
            self.isSelectedChip = flag

        with source.addIfTask(lambda: self.isSelectedChip is True) as (source_true, source_false):
            with source_true.addIfTask(lambda: chip.selected is True) as (true, false):
                true.addFunction(chipSelected, False)
                true.addFunction(self.setChipInLastFrame, chip, False)

                movie_type_true = chip.movie.getType()
                if movie_type_true == "ObjectMovie2":
                    true.addTask("TaskMovie2Play", Movie2=chip.movie, Wait=True, Loop=False)
                elif movie_type_true == "ObjectMovie":
                    true.addTask("TaskMoviePlay", Movie=chip.movie, Wait=True, Loop=False)

                # true.addNotify(Notificator.onSoundEffectOnObject, self.object,
                #                "SwapChipsSwitchEnableAndDisable_PutBack")

                false.addFunction(chipSelected, True)

                movie_type_false = selectedList[slot.id].movie.getType()
                if movie_type_false == "ObjectMovie2":
                    false.addTask("TaskMovie2Play", Movie2=selectedList[slot.id].movie, Wait=True, Loop=False)
                elif movie_type_false == "ObjectMovie":
                    false.addTask("TaskMoviePlay", Movie=selectedList[slot.id].movie, Wait=True, Loop=False)

                false.addFunction(self.setIsSelectedChips)
                false.addScope(self.changeAlpha, 1.0, 0.0)
                false.addNotify(Notificator.onSoundEffectOnObject, self.object, "SwapChipsSwitchEnableAndDisable_SwapChips")
                false.addFunction(self.swap)
                false.addScope(self.changeAlpha, 0.0, 1.0)
                false.addScope(self.playMovie)

            source_false.addFunction(chipSelected, True)

            movie_type_false2 = selectedList[slot.id].movie.getType()
            if movie_type_false2 == "ObjectMovie2":
                source_false.addTask("TaskMovie2Play", Movie2=selectedList[slot.id].movie, Wait=True, Loop=False)
            elif movie_type_false2 == "ObjectMovie":
                source_false.addTask("TaskMoviePlay", Movie=selectedList[slot.id].movie, Wait=True, Loop=False)

    def setIsSelectedChips(self):
        def isSelectedChips():
            chips = []
            for chip in self.visibleChips:
                if chip.selected is True:
                    chips.append(chip)
            return chips

        self.isSelectedChipsList = isSelectedChips()

    def changeAlpha(self, source, From, To):
        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addTask("TaskNodeAlphaTo", Node=self.isSelectedChipsList[0].slot.slot, From=From, To=To, Time=400)
            parallel_2.addTask("TaskNodeAlphaTo", Node=self.isSelectedChipsList[1].slot.slot, From=From, To=To, Time=400)

    def playMovie(self, source):
        Chip_1 = self.visibleChips[len(self.visibleChips) - 1]
        Chip_2 = self.visibleChips[len(self.visibleChips) - 2]

        movie_type_chip1 = Chip_1.movie.getType()
        movie_type_chip2 = Chip_2.movie.getType()

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            # parallel_1.addTask("TaskMovieLastFrame", Movie=Chip_1.movie, Value=False)
            parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, "SwapChipsSwitchEnableAndDisable_PutBack")

            if movie_type_chip1 == "ObjectMovie2":
                parallel_1.addTask("TaskMovie2Play", Movie2=Chip_1.movie)
            elif movie_type_chip1 == "ObjectMovie":
                parallel_1.addTask("TaskMoviePlay", Movie=Chip_1.movie)

            # parallel_2.addTask("TaskMovieLastFrame", Movie=Chip_2.movie, Value=False)
            parallel_2.addNotify(Notificator.onSoundEffectOnObject, self.object, "SwapChipsSwitchEnableAndDisable_PutBack")

            if movie_type_chip2 == "ObjectMovie2":
                parallel_2.addTask("TaskMovie2Play", Movie2=Chip_2.movie)
            elif movie_type_chip2 == "ObjectMovie":
                parallel_2.addTask("TaskMoviePlay", Movie=Chip_2.movie)


    def disableNotUsedChips(self):
        def disable(list):
            for (_, chip) in list.iteritems():
                if chip in self.visibleChips:
                    chip.movie.setEnable(True)
                else:
                    chip.movie.setEnable(False)

        disable(self.redChips)
        disable(self.blueChips)
        disable(self.greenChips)
        disable(self.blackChips)

    def swap(self):
        chips = []
        for chip in self.visibleChips:
            if chip.selected is True:
                chips.append(chip)
        chip_1, chip_2 = chips

        analog1 = self.searchChip(chip_2.type, chip_1.slot)
        analog2 = self.searchChip(chip_1.type, chip_2.slot)
        # analog1.node.setWorldPosition((0, 0))
        # analog2.node.setWorldPosition((0, 0))
        chip_1.node.removeFromParent()
        chip_2.node.removeFromParent()

        self.setChipInLastFrame(chip_1, False)
        self.setChipInLastFrame(chip_2, False)

        chip_1.slot.slot.addChild(analog1.node)
        chip_2.slot.slot.addChild(analog2.node)

        chip_1.selected = False
        chip_2.selected = False
        self.isSelectedChip = False

        self.visibleChips.remove(chip_1)
        self.visibleChips.remove(chip_2)
        self.visibleChips.append(analog1)
        self.visibleChips.append(analog2)
        self.disableNotUsedChips()

        self.Unselected_All()

    def Unselected_All(self):
        self.disableSelectedSlots(self.selectedBlueChips)
        self.disableSelectedSlots(self.selectedRedChips)
        self.disableSelectedSlots(self.selectedGreenChips)
        self.disableSelectedSlots(self.selectedBlackChips)

    def disableSelectedSlots(self, dict):
        for (_, light) in dict.iteritems():
            light.movie.setEnable(False)

    def getCorrectChipsList(self, type):
        if type == 'Red':
            return self.redChips, self.selectedRedChips
        elif type == 'Blue':
            return self.blueChips, self.selectedBlueChips
        elif type == 'Green':
            return self.greenChips, self.selectedGreenChips
        elif type == 'Black':
            return self.blackChips, self.selectedBlackChips

    def searchChip(self, type, slot):
        chipsList = self.getCorrectChipsList(type)[0]
        return chipsList[slot.id]

    def checkWin(self):
        def checkSlotChack(slots):
            checkSlots = []
            for slotNum in slots:
                if (slotNum <= 12) and (slotNum >= 1):
                    for slot in self.slots:
                        if slot.id == slotNum:
                            checkSlots.append(slot)
            return checkSlots

        def searchChips(checkSlots):
            chips = []
            for slot in checkSlots:
                for visChip in self.visibleChips:
                    if visChip.slotID == slot.id:
                        chips.append(visChip)
            return chips

        flag = True
        for chip in self.visibleChips:
            slots = [chip.slotID - 1, chip.slotID + 1, chip.slotID - 4, chip.slotID + 4]
            if chip.slotID == 4 or chip.slotID == 8:
                slots.pop(1)
            elif chip.slotID == 5 or chip.slotID == 9:
                slots.pop(0)
            checkSlots = checkSlotChack(slots)
            checkChips = searchChips(checkSlots)
            for checkChip in checkChips:
                if checkChip.type == chip.type:
                    flag = False
                    break
            if flag is False:
                break
        if flag is True:
            self.complete()

    def complete(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for slot in self.slots:
            socket = slot.movie.getSocket('slot')
            socket.disable()

        for chip in self.visibleChips:
            self.object.setVisibleChips(chip.slotID, chip.type)
        self.object.setParam('finishFlag', True)

        self.enigmaComplete()

    def _skipEnigma(self):
        self.disableNotUsedChips()
        self.Unselected_All()
        self.complete()

    # ==================================================================================================================

    # -------------- Clean ---------------------------------------------------------------------------------------------
    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.param = None

        def cleanList(list):
            for (_, chip) in list.iteritems():
                chip.node.removeFromParent()
            list.clear()

        cleanList(self.redChips)
        cleanList(self.blueChips)
        cleanList(self.greenChips)
        cleanList(self.blackChips)
        cleanList(self.selectedRedChips)
        cleanList(self.selectedBlueChips)
        cleanList(self.selectedBlackChips)
        cleanList(self.selectedGreenChips)

        for chip in self.slots:
            chip.node.removeFromParent()
            chip.movie.getEntityNode().removeFromParent()
        self.slots = []

        self.visibleChips = []
        self.isSelectedChip = False

    # ==================================================================================================================
