from Event import Event
from Foundation.TaskManager import TaskManager
from HOPA.StonePyramidsManager import StonePyramidsManager
from Holder import Holder

Enigma = Mengine.importEntity("Enigma")

class Stone(object):
    def __init__(self, slot_name, slot, slot_to_name, movie_start, movie_select, movie_finish, movie_fall):
        movie_start.setEnable(False)
        movie_select.setEnable(False)
        movie_fall.setEnable(False)
        movie_finish.setEnable(False)

        self.slot_name = slot_name
        self.slot = slot
        self.slot_to_name = slot_to_name

        self.movie_start = movie_start
        self.movie_select = movie_select
        self.movie_finish = movie_finish
        self.movie_fall = movie_fall

        self.picked = False
        self.placed = False

        self.__tc_select = None
        self.__tc_pulse = None
        self.__movie_select_enabled_event = Event("SelectMovieEnabled")
        self.__pulse_end_event = Event("MovieSelectPulseEnd")

    def enableSelectTC(self):
        if self.placed:
            return

        self.movie_start.setEnable(True)
        if self.picked:
            # if stone was picked and not placed then movie fall was played, and we should play respawn anim
            self.picked = False
            self.movie_start.setPlay(True)
        else:
            self.movie_start.setLastFrame(True)

        self.movie_select.setEnable(False)

        self.__tc_select = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_select as tc:
            # select
            tc.addTask("TaskMovie2SocketEnter", Movie2=self.movie_start, SocketName='socket')
            tc.addDisable(self.movie_start)
            tc.addEnable(self.movie_select)
            tc.addFunction(self.movie_select.setPlay, True)
            tc.addFunction(self.__movie_select_enabled_event)

            # deselect
            tc.addTask("TaskMovie2SocketLeave", Movie2=self.movie_select, SocketName='socket')
            tc.addFunction(self.movie_select.setLastFrame, True)
            tc.addFunction(self.movie_select.setPlay, False)
            tc.addDisable(self.movie_select)
            tc.addEnable(self.movie_start)

    def disableSelectTC(self):
        if self.__tc_select is not None:
            self.__tc_select.cancel()
            self.__tc_select = None

        if self.picked:
            self.movie_start.setEnable(False)
            self.movie_select.setEnable(False)

    def scopeSocketClick(self, source):
        if self.movie_select.getEnable() is False:
            source.addEvent(self.__movie_select_enabled_event)
        source.addTask("TaskMovie2SocketClick", Movie2=self.movie_select, SocketName='socket')

    def setPicked(self, picked):
        self.picked = picked

    def setPlaced(self, placed):
        self.placed = placed

    def enablePulseTC(self):
        self.movie_select.setEnable(True)
        node = self.movie_select.getEntityNode()

        self.__tc_pulse = TaskManager.createTaskChain()
        with self.__tc_pulse as tc:
            with tc.addRepeatTask() as (repeat, until):
                repeat.addTask("TaskNodeAlphaTo", Node=node, To=0.5, Time=500, Interrupt=True)
                repeat.addTask("TaskNodeAlphaTo", Node=node, To=1.0, Time=500, Interrupt=True)
                until.addEvent(self.__pulse_end_event)

        # Why alpha?  # play movie_select in loop cause sound problems  # scale looks terrible because of anchor which is not at the center of stone

    def disablePulseTC(self):
        self.__pulse_end_event()
        self.movie_select.setAlpha(1.0)
        self.movie_select.setEnable(False)

        if self.__tc_pulse is not None:
            self.__tc_pulse.cancel()
            self.__tc_pulse = None

    def cleanUp(self):
        if Mengine.hasTouchpad():
            self.disablePulseTC()
            self.movie_start.returnToParent()
            self.movie_select.returnToParent()

        self.disableSelectTC()

class Pyramid(object):
    STONES_PLATE_MOVIE = None
    UPDATE_PYRAMID_DIST_INFO_EVENT = Event('StonePyramidsPickPyramidEvent')
    PYRAMID_ALPHA_TO = 0.5
    PYRAMID_ALPHA_FROM = 1.0
    PYRAMID_ALPHA_TIME = 300

    def __init__(self, slot_name, slot, virtual_slot, stones_slot_names_stack):
        self.slot_name = slot_name
        self.slot = slot

        virtual_slot.setName(slot_name)
        virtual_slot.enable()
        self.virtual_slot = virtual_slot

        self.stones_slot_names_stack = stones_slot_names_stack
        self.slot_stack = [self.virtual_slot, ]

        self.complete = False

        self.__tc_alpha_to = None
        self.__tc_alpha_from = None

    def getLastSlot(self):
        if len(self.slot_stack) == 1:
            self.virtual_slot.setLocalPosition(self.slot.getWorldPosition())
        return self.slot_stack[-1]

    def stonesSlotStackInsert(self, stone):
        slot_stack_size = len(self.slot_stack)
        if self.stones_slot_names_stack[slot_stack_size - 1] == stone.slot_to_name:
            self.slot_stack.append(stone.slot)
            self.complete = slot_stack_size == len(self.stones_slot_names_stack)
            stone.setPlaced(True)
            return True
        else:
            return False

    def enableTransparencyTC(self):
        self.__tc_alpha_to = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_alpha_to as tc:
            tc.addEvent(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT, lambda pyramid_list: pyramid_list[0] is self)
            tc.addDelay(1)

            with tc.addRaceTask(2) as (alpha_to, interrupt):
                alpha_to.addTask("TaskNodeAlphaTo", Node=self.virtual_slot, To=Pyramid.PYRAMID_ALPHA_TO, Time=Pyramid.PYRAMID_ALPHA_TIME, Interrupt=True)
                interrupt.addEvent(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT, lambda pyramid_list: pyramid_list[0] is not self)

        self.__tc_alpha_from = TaskManager.createTaskChain(Repeat=True)
        with self.__tc_alpha_from as tc:
            tc.addEvent(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT, lambda pyramid_list: pyramid_list[0] is not self)
            tc.addDelay(1)

            with tc.addRaceTask(2) as (alpha_from, interrupt):
                alpha_from.addTask("TaskNodeAlphaTo", Node=self.virtual_slot, To=Pyramid.PYRAMID_ALPHA_FROM, Time=Pyramid.PYRAMID_ALPHA_TIME, Interrupt=True)
                interrupt.addEvent(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT, lambda pyramid_list: pyramid_list[0] is self)

    def disableTransparencyTC(self):
        if self.__tc_alpha_to is not None:
            self.__tc_alpha_to.cancel()

        if self.__tc_alpha_from is not None:
            self.__tc_alpha_from.cancel()

        self.virtual_slot.getRender().setLocalAlpha(self.PYRAMID_ALPHA_FROM)

    def cleanUp(self):
        self.disableTransparencyTC()

        self.slot_stack.reverse()

        for slot in self.slot_stack:
            if slot is None:
                continue
            slot.removeChildren()

        self.virtual_slot.removeFromParent()
        Mengine.destroyNode(self.virtual_slot)
        self.virtual_slot = None

class StonePyramids(Enigma):
    def __init__(self):
        super(StonePyramids, self).__init__()
        self.tc_main = None
        self.tc_pick_pyramid = None

        self.params = None

        self.stones = dict()
        self.pyramids = dict()

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def loadParam(self):
        self.params = StonePyramidsManager.getParam(self.EnigmaName)

    def setup(self):
        for slot_to_name, stone_param in self.params.stones.items():
            movie_start = self.object.getObject(stone_param['Start'])
            movie_select = self.object.getObject(stone_param['Select'])
            movie_finish = self.object.getObject(stone_param['Finish'])
            movie_fall = self.object.getObject(stone_param['Fall'])

            slot_name = str()
            slot = None
            for (movie_finish_, slot_name, slot) in movie_finish.entity.movie.getSlots():
                slot_name = slot_name
                slot = slot

            stone = Stone(slot_name, slot, slot_to_name, movie_start, movie_select, movie_finish, movie_fall)
            self.stones[slot_to_name] = stone

        Pyramid.PYRAMID_ALPHA_TO = self.params.pyramid_alpha_to
        Pyramid.PYRAMID_ALPHA_FROM = self.params.pyramid_alpha_from
        Pyramid.PYRAMID_ALPHA_TIME = self.params.pyramid_alpha_time

        Pyramid.STONES_PLATE_MOVIE = self.object.getObject(self.params.stones_plate)
        for (stone_plate_movie, slot_name, slot) in Pyramid.STONES_PLATE_MOVIE.entity.movie.getSlots():
            stones_slot_names_stack = list()

            stone_slot_name = slot_name
            while bool(stone_slot_name):
                stones_slot_names_stack.append(stone_slot_name)
                stone_slot_name = self.stones[stone_slot_name].slot_name

            virtual_slot = Mengine.createNode('Interender')
            self.addChild(virtual_slot)

            pyramid = Pyramid(slot_name, slot, virtual_slot, stones_slot_names_stack)
            self.pyramids[slot_name] = pyramid

        self.attachStonesToMobilePositions()

    def attachStonesToMobilePositions(self):
        """ Attach stones to movie with new positions if it is a mobile device and MG in zoom (must be Layer2D_Over) """
        if self.params.mobile_positions_movie_name is None:
            return

        if self.object.parent.hasObject(self.params.mobile_positions_movie_name) is False:
            return
        attach_movie = self.object.parent.getObject(self.params.mobile_positions_movie_name)

        if Mengine.hasTouchpad() is False:
            attach_movie.setEnable(False)
            return

        for stone in self.stones.values():
            slot = attach_movie.getMovieSlot(stone.slot_to_name)

            affected_movies = [stone.movie_start, stone.movie_select]
            for movie in affected_movies:
                node = movie.getEntityNode()
                node.removeFromParent()
                slot.addChild(node)

        attach_movie.setEnable(True)
        attach_movie.setInteractive(True)

    def cleanUp(self):
        if self.tc_main is not None:
            self.tc_main.cancel()
            self.tc_main = None

        if self.tc_pick_pyramid is not None:
            self.tc_pick_pyramid.cancel()
            self.tc_pick_pyramid = None

        if self.object.parent.hasObject(self.params.mobile_positions_movie_name) is True:
            attach_movie = self.object.parent.getObject(self.params.mobile_positions_movie_name)
            attach_movie.setEnable(False)

        for stone in self.stones.values():
            stone.cleanUp()
        self.stones = {}

        for pyramid in self.pyramids.values():
            pyramid.cleanUp()
        self.pyramids = {}

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def setPyramidHolder(self, pyramids_list_by_dist_holder, pyramid_holder):
        """ sets pyramid in `pyramid_holder` using `pyramids_list_by_dist_holder`, returns found pyramid """
        pyramids_list_by_dist = pyramids_list_by_dist_holder.get()
        pyramid = None

        for pyramid_ in pyramids_list_by_dist:
            # if last slot is none, pyramid construction finished, we should get next nearest pyramid
            if pyramid_.getLastSlot() is not None:
                pyramid = pyramid_
                break

        pyramid_holder.set(pyramid)
        return pyramid

    def scopePickStone(self, source, stone_holder):
        for (stone_slot_to, stone), race in source.addRaceTaskList(self.stones.iteritems()):
            race.addScope(stone.scopeSocketClick)
            race.addFunction(stone_holder.set, stone)
            race.addFunction(stone.setPicked, True)

    def scopeAttachStoneDefault(self, source, stone_holder, pyramids_list_by_dist_holder, pyramid_holder, attach_stone_first_time_holder):
        stone = stone_holder.get()
        movie_finish = stone.movie_finish
        movie_finish_node = movie_finish.getEntityNode()
        movie_finish.setEnable(True)

        pyramid = self.setPyramidHolder(pyramids_list_by_dist_holder, pyramid_holder)
        slot = pyramid.getLastSlot()

        anchor = movie_finish_node.getLocalOrigin()
        temp_anchor = anchor + self.params.stone_anchor_shift_on_magnet

        source.addFunction(movie_finish_node.setLocalOrigin, temp_anchor)  # set new anchor
        source.addFunction(slot.addChild, movie_finish_node)

        if attach_stone_first_time_holder.get():
            source.addTask("TaskNodeAlphaTo", Node=movie_finish_node, From=Pyramid.PYRAMID_ALPHA_TO, To=Pyramid.PYRAMID_ALPHA_FROM, Time=Pyramid.PYRAMID_ALPHA_TIME)

    def scopeAttachStoneTouchpad(self, source, stone_holder, pyramids_list_by_dist_holder, pyramid_holder):
        stone = stone_holder.get()
        movie_finish = stone.movie_finish
        movie_finish_node = movie_finish.getEntityNode()
        movie_finish.setEnable(True)

        pyramid = self.setPyramidHolder(pyramids_list_by_dist_holder, pyramid_holder)
        slot = pyramid.getLastSlot()

        source.addFunction(slot.addChild, movie_finish_node)
        source.addTask("TaskNodeAlphaTo", Node=movie_finish_node, From=Pyramid.PYRAMID_ALPHA_TO, To=Pyramid.PYRAMID_ALPHA_FROM, Time=Pyramid.PYRAMID_ALPHA_TIME)

    def scopeDetachStone(self, source, stone_holder):
        stone = stone_holder.get()
        movie_finish = stone.movie_finish
        movie_finish_node = movie_finish.getEntityNode()

        anchor = movie_finish_node.getLocalOrigin()
        original_anchor = anchor - self.params.stone_anchor_shift_on_magnet

        source.addFunction(movie_finish_node.setLocalOrigin, original_anchor)  # restore old anchor

    def scopePlaceStone(self, source, stone_holder, pyramid_holder):
        stone = stone_holder.get()
        movie_finish = stone.movie_finish
        movie_finish_node = movie_finish.getEntityNode()
        movie_fall = stone.movie_fall
        movie_fall_node = movie_fall.getEntityNode()

        pyramid = pyramid_holder.get()
        slot = pyramid.getLastSlot()

        source.addTask("TaskMovie2Play", Movie2=movie_finish, Wait=True)

        with source.addIfTask(pyramid.stonesSlotStackInsert, stone) as (_, false):
            false.addDisable(movie_finish)
            false.addFunction(self.node.addChild, movie_finish_node)  # restore movie finish parent

            false.addFunction(slot.addChild, movie_fall_node)  # temporary attach to pyramid slot
            false.addEnable(stone.movie_fall)
            false.addTask("TaskMovie2Play", Movie2=stone.movie_fall, Wait=True)
            false.addDisable(movie_fall)
            false.addFunction(self.node.addChild, movie_fall_node)  # restore movie fall parent

    def enableHighlightStoneTC(self, enable):
        if enable:
            for stone in self.stones.values():
                stone.enableSelectTC()
        else:
            for stone in self.stones.values():
                stone.disableSelectTC()

    def scopeFindNearestPyramid(self, source, pyramids_list_by_dist_holder):
        cursor_pos = Mengine.getCursorPosition()
        pyramid_slot_dists = list()

        for pyramid_base_slot_name, pyramid in self.pyramids.items():
            slot = pyramid.getLastSlot()

            if slot is None:  # mean final stone is placed, measure distance from prev slot in stack
                slot = pyramid.slot_stack[-2]

            slot_pos = slot.getWorldPosition()
            slot_cursor_horizontal_dist = abs(cursor_pos.x - slot_pos.x)
            pyramid_slot_dists.append((slot_cursor_horizontal_dist, pyramid))

        pyramid_slot_dists.sort()
        pyramid_slot_dists = [pyramid for (dist, pyramid) in pyramid_slot_dists]

        source.addFunction(pyramids_list_by_dist_holder.set, pyramid_slot_dists)
        source.addFunction(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT, pyramid_slot_dists)

    def enableFindNearestPyramidTC(self, enable, pyramids_list_by_dist_holder):
        if enable:
            self.tc_pick_pyramid = TaskManager.createTaskChain(Repeat=True)
            with self.tc_pick_pyramid as tc:
                tc.addTask("TaskMouseMove", Tracker=lambda *_: True)
                tc.addScope(self.scopeFindNearestPyramid, pyramids_list_by_dist_holder)
        else:
            self.tc_pick_pyramid.cancel()

    def enablePyramidTransparencyTC(self, enable):
        if Mengine.hasTouchpad() is True:
            return
        if enable:
            for pyramid in self.pyramids.values():
                pyramid.enableTransparencyTC()
        else:
            for pyramid in self.pyramids.values():
                pyramid.disableTransparencyTC()

    def enableSelectedStonePulseTC(self, enable, stone_holder):
        stone = stone_holder.get()
        if enable:
            stone.enablePulseTC()
        else:
            stone.disablePulseTC()

    def runTaskChains(self):
        stone_holder = Holder()
        pyramids_list_by_dist_holder = Holder()
        pyramid_holder = Holder()

        def _scopeDefaultBehaviour(source):
            attach_stone_first_time_holder = Holder()
            attach_stone_first_time_holder.set(True)

            with source.addRepeatTask() as (repeat, until):
                # attach stone finish_movie
                repeat.addScope(self.scopeAttachStoneDefault, stone_holder, pyramids_list_by_dist_holder, pyramid_holder, attach_stone_first_time_holder)
                repeat.addEvent(Pyramid.UPDATE_PYRAMID_DIST_INFO_EVENT)
                repeat.addScope(self.scopeDetachStone, stone_holder)  # dettach stone finish_movie
                repeat.addFunction(attach_stone_first_time_holder.set, False)

                until.addTask("TaskMouseButtonClick", isDown=True)  # click for stone placing
                until.addTask("TaskMouseButtonClick", isDown=False)
                until.addScope(self.scopeDetachStone, stone_holder)
                until.addFunction(attach_stone_first_time_holder.set, True)

        def _scopeTouchpadBehaviour(source):
            source.addTask("TaskMouseButtonClick", isDown=True)  # click for stone placing
            source.addTask("TaskMouseButtonClick", isDown=False)
            source.addScope(self.scopeAttachStoneTouchpad, stone_holder, pyramids_list_by_dist_holder, pyramid_holder)

        self.tc_main = TaskManager.createTaskChain(Repeat=True)
        with self.tc_main as tc:
            tc.addFunction(self.enableHighlightStoneTC, True)
            tc.addFunction(self.enableFindNearestPyramidTC, True, pyramids_list_by_dist_holder)
            tc.addFunction(self.enablePyramidTransparencyTC, True)

            tc.addScope(self.scopePickStone, stone_holder)  # click for stone select

            tc.addFunction(self.enableHighlightStoneTC, False)
            tc.addFunction(self.enablePyramidTransparencyTC, False)

            if Mengine.hasTouchpad():
                tc.addFunction(self.enableSelectedStonePulseTC, True, stone_holder)
                tc.addScope(_scopeTouchpadBehaviour)
                tc.addFunction(self.enableSelectedStonePulseTC, False, stone_holder)
            else:
                tc.addScope(_scopeDefaultBehaviour)

            tc.addFunction(self.enableFindNearestPyramidTC, False, pyramids_list_by_dist_holder)

            tc.addScope(self.scopePlaceStone, stone_holder, pyramid_holder)  # play stone finish_movie or fall_movie

            tc.addFunction(lambda: self.enigmaComplete() if all([pyramid.complete for pyramid in self.pyramids.values()]) else None)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(StonePyramids, self)._onPreparation()
        self.loadParam()
        self.setup()

    def _onActivate(self):
        super(StonePyramids, self)._onActivate()

    def _onDeactivate(self):
        super(StonePyramids, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.runTaskChains()

    def _stopEnigma(self):
        self.cleanUp()

    def _restoreEnigma(self):
        self.runTaskChains()

    def _resetEnigma(self):
        self.cleanUp()
        self.setup()
        self.runTaskChains()

    def _skipEnigma(self):
        return