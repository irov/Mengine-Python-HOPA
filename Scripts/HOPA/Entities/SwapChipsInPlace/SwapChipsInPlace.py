import math

from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.SwapChipsInPlaceManager import SwapChipsInPlaceManager


Enigma = Mengine.importEntity("Enigma")


class SwapChipsInPlace(Enigma):
    class Chip(object):
        def __init__(self, id_, movie, place, movie_idle, movie_selected, allowed_move):
            self.id = id_
            self.movie = movie
            self.movie_idle = movie_idle
            self.movie_selected = movie_selected
            self.place = place
            self.node = self.movie_idle.getEntityNode()
            self.selected = False
            self.allowed = allowed_move

    class Place(object):
        def __init__(self, ID, movie):
            self.id = ID
            self.movie = movie
            self.slot = self.movie.getMovieSlot('slot')

    def __init__(self):
        super(SwapChipsInPlace, self).__init__()
        self.tc = None
        self.param = None
        self.chips = {}
        self.places = {}
        self.selected_chip = None

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction('completeEnigma')

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(SwapChipsInPlace, self)._onPreparation()

    def _onActivate(self):
        super(SwapChipsInPlace, self)._onActivate()
        if self.object.getParam('completeEnigma') is True:
            for place in self.places:
                socket = place.movie.getSocket('place')
                socket.disable()

    def _onDeactivate(self):
        super(SwapChipsInPlace, self)._onDeactivate()
        self.__cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.__loadParam()
        self.__setupChips()
        self.__runTaskChain()

    def _restoreEnigma(self):
        self.__cleanUp()
        self._playEnigma()

    def _resetEnigma(self):
        self.__cleanUp()
        self._playEnigma()

    def _skipEnigma(self):
        self.__cleanUp()
        self.object.setParam('completeEnigma', True)

    def _stopEnigma(self):
        self.__cleanUp()

    # ==================================================================================================================

    def __loadParam(self):
        self.param = SwapChipsInPlaceManager.getParam(self.EnigmaName)

    def __setupChips(self):
        group_name = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        group = GroupManager.getGroup(group_name)

        for (place_id, movie_name) in self.param.Places.iteritems():
            movie = group.getObject(movie_name)
            place = SwapChipsInPlace.Place(place_id, movie)
            socket = place.movie.getSocket('place')
            socket.enable()
            self.places[place_id] = place

        self.rotates = self.param.Rotates

        for (chip_id, (movie_name, movie_idle_name, movie_selected_name, allowed_move, start_angle)) in self.param.Chips.iteritems():
            movie_chip = None
            movie_selected = None
            if movie_name is not None:
                movie_chip = group.getObject(movie_name)
                movie_chip.setEnable(False)
            if movie_selected_name is not None:
                movie_selected = group.getObject(movie_selected_name)
                movie_selected.setEnable(False)

            movie_idle = group.getObject(movie_idle_name)
            movie_idle.setEnable(True)
            movie_idle.setLastFrame(False)
            place_id = self.param.startComb[chip_id]
            place = self.places[place_id]
            chip = SwapChipsInPlace.Chip(chip_id, movie_chip, place, movie_idle, movie_selected, allowed_move)

            self.chips[chip_id] = chip
            self.__setupChipOnPlace(chip, Angle=start_angle)

    def __setupChipOnPlace(self, *chips, **kwg):
        for i, chip in enumerate(chips):
            chip.node.setLocalPosition((0, 0))
            chip.place.slot.addChild(chip.node)
            angle = kwg.get("Angle", self.rotates.get((chip.id, chip.place.id), 0))
            if isinstance(angle, list):
                angle = angle[i]
            chip.place.slot.setAngle(angle)

            if chip.movie_selected is not None:
                node_selected = chip.movie_selected.getEntityNode()
                chip.place.slot.addChild(node_selected)

    def __runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.__scopeClick)

    def __scopeClick(self, source):
        click_place = Holder()
        for (_, place), click in source.addRaceTaskList(self.places.iteritems()):
            click.addTask('TaskMovie2SocketClick', Movie2=place.movie, SocketName='place')
            click.addFunction(click_place.set, place)

        def __scopeClickReadHolder(source_holder, holder):
            click_place_holder = holder.get()
            source_holder.addScope(self._scopeResloveClick, click_place_holder)

        source.addScope(__scopeClickReadHolder, click_place)

    def _scopeResloveClick(self, source, place):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapChipsInPlace_ClickOnChip')
        chip = None
        for (_, check_chip) in self.chips.iteritems():
            if check_chip.place == place:
                chip = check_chip

        with source.addIfTask(lambda: self.selected_chip is not None) as (true, false):
            with true.addIfTask(lambda: chip.selected is True) as (true_true, true_false):
                with true_true.addParallelTask(2) as (scale_reduce, sound_effect):
                    scale_reduce.addScope(self.__scopeSetSelectStatus, chip, False)
                    sound_effect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapChipsInPlace_ScaleReduce')

                with true_false.addIfTask(lambda: chip.allowed is True or self.selected_chip.allowed is True) as (allowed, not_allowed):
                    allowed.addScope(self.__scopeSetSelectStatus, chip, True)
                    allowed.addScope(self.__scopeMoveChips, chip)

                with true_false.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addScope(self.__scopeSetSelectStatus, chip, False)
                    parallel_2.addScope(self.__scopeSetSelectStatus, self.selected_chip, False)

            false.addScope(self.__scopeSetSelectStatus, chip, True)
        source.addFunction(self.__checkWinsCombination)

    def __scopeSetSelectStatus(self, source, chip, flag):
        chip.selected = flag

        if flag is True and self.selected_chip is None:
            self.selected_chip = chip
        elif flag is False and self.selected_chip is not None:
            if self.selected_chip.allowed is False and chip.allowed is False:
                if chip.id != self.selected_chip.id:
                    self.selected_chip = None
                    return
            self.selected_chip = None

        if chip.movie_selected is not None:
            if flag is False:
                chip.movie_idle.setEnable(False)
                chip.movie_selected.setEnable(True)
                movie = chip.movie_selected
                pos = chip.node.getWorldPosition()
                node = movie.getEntityNode()
                node.setWorldPosition(pos)
            else:
                chip.movie_idle.setEnable(True)
                chip.movie_selected.setEnable(False)
                movie = chip.movie_idle

            source.addTask("TaskMovie2Play", Movie2=movie, Wait=True)
            return

        scale_time = DefaultManager.getDefaultFloat('SwapChipsInPlace_ScaleTime', 1000)
        scale_to = DefaultManager.getDefaultTuple('SwapChipsInPlace_ScaleTo', (1.2, 1.2, 1.2))

        with source.addIfTask(lambda: flag is True) as (true, false):
            true.addTask('TaskNodeScaleTo', Node=chip.node, To=scale_to, Time=scale_time)
            false.addTask('TaskNodeScaleTo', Node=chip.node, To=(1.0, 1.0, 1.0), Time=scale_time)

    def __scopeMoveChips(self, source, chip):
        source.addScope(self.__scopeMoveChip, chip)
        source.addScope(self.__scopeSwapChips, chip)

    def __scopeMoveChip(self, source, chip):
        def __setup_chip_on_top(chip_on_top):
            pos = chip_on_top.node.getWorldPosition()
            chip_on_top.node.removeFromParent()
            node = self.object.getEntityNode()
            node.addChild(chip_on_top.node)
            chip_on_top.node.setWorldPosition(pos)

        time = DefaultManager.getDefaultFloat('SwapChipsInPlace_MoveChipTime', 700.0)
        bezier = DefaultManager.getDefaultFloat('SwapChipsInPlace_MoveChipBezier', 3.75)

        chip_1 = self.selected_chip
        chip_2 = chip

        __setup_chip_on_top(chip_1)
        __setup_chip_on_top(chip_2)

        chip_1_pos = chip_1.node.getWorldPosition()
        chip_2_pos = chip_2.node.getWorldPosition()

        x = chip_1_pos.x - chip_2_pos.x
        p1 = ((chip_1_pos.x + chip_2_pos.x) / 2, ((chip_1_pos.y + chip_2_pos.y) / 2) - abs(x) / bezier)

        chip_1_old_angle = chip_1.node.getAngle()
        chip_2_old_angle = chip_2.node.getAngle()

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            with parallel_1.addParallelTask(2) as (parallel_1_1, parallel_1_2):
                parallel_1_1.addTask("TaskNodeBezier2To", Node=chip_1.node, Point1=p1, To=chip_2_pos, Time=time)

                parallel_1_2.addScope(self.__scopeRotateChip, chip_1, chip_1.node, time=1, angle=chip_1_old_angle)

                parallel_1_2.addScope(self.__scopeRotateChip, chip_1, chip_1.node, time=time,
                                      angle=self.rotates.get((chip_1.id, chip_2.place.id)))

                parallel_1_2.addScope(self.__scopeRotateChip, chip_1, chip_1.node, time=1, angle=chip_1_old_angle)

            with parallel_2.addParallelTask(2) as (parallel_2_1, parallel_2_2):
                parallel_2_1.addTask("TaskNodeBezier2To", Node=chip_2.node, Point1=p1, To=chip_1_pos, Time=time)

                parallel_2_2.addScope(self.__scopeRotateChip, chip_2, chip_2.node, time=1, angle=chip_2_old_angle)

                parallel_2_2.addScope(self.__scopeRotateChip, chip_2, chip_2.node, time=time,
                                      angle=self.rotates.get((chip_2.id, chip_1.place.id)))

                parallel_2_2.addScope(self.__scopeRotateChip, chip_2, chip_2.node, time=1, angle=chip_2_old_angle)

    def __scopeSwapChips(self, source, chip):
        def __swap_chips_places(chip1, chip2):
            chip1.place, chip2.place = chip2.place, chip1.place

        chip_1 = self.selected_chip
        chip_2 = chip

        if chip_1.allowed is True or chip_2.allowed is True:
            source.addFunction(chip_1.node.removeFromParent)
            source.addFunction(chip_2.node.removeFromParent)

            source.addFunction(__swap_chips_places, chip_1, chip_2)
            source.addFunction(self.__setupChipOnPlace, chip_1, chip_2)

            with source.addParallelTask(2) as (source_chip_1, source_chip_2):
                source_chip_1.addScope(self.__scopeRotateChip, chip_1, chip_2.place.slot)

                source_chip_2.addScope(self.__scopeRotateChip, chip_2, chip_1.place.slot)

    def __scopeRotateChip(self, source, chip, node, time=1, angle=None):
        if angle is None:
            angle = self.rotates.get((chip.id, chip.place.id), 0)
        source.addTask('TaskNodeRotateTo', Node=node, To=angle * math.pi / 180, Time=time)

    def __checkWinsCombination(self):
        flag = True
        for (chipID, placeID) in self.param.winsComb.iteritems():
            if self.chips[chipID].place == self.places[placeID]:
                if self.chips[chipID].movie is not None:
                    self.chips[chipID].movie.setEnable(True)
                continue

            if self.chips[chipID].movie is not None:
                self.chips[chipID].movie.setEnable(False)
            flag = False

        if flag is True:
            self.__complete()

    def __complete(self):
        self.__cleanUp()
        self.object.setParam('completeEnigma', True)
        self.enigmaComplete()

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.param = None
        self.selected_chip = None

        for (_, place) in self.places.iteritems():
            socket = place.movie.getSocket('place')
            socket.disable()

        for (_, chip) in self.chips.iteritems():
            chip.movie_idle.returnToParent()
            chip.movie_idle.setEnable(False)

            if chip.movie is not None:
                chip.movie.setEnable(False)

            if chip.movie_selected is not None:
                chip.movie_selected.returnToParent()
                chip.movie_selected.setEnable(False)

        self.chips = {}
        self.places = {}
