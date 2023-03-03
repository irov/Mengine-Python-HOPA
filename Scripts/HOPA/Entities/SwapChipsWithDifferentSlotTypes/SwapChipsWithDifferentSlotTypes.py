from Event import Event
from Foundation import Utils
from Foundation.Notificator import Notificator
from Foundation.Task.TaskGenerator import TaskSource
from Foundation.TaskManager import TaskManager
from HOPA.SwapChipsWithDifferentSlotTypesManager import SwapChipsWithDifferentSlotTypesManager
from Holder import Holder
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")

SOCKET_CLICK_EVENT = Event('SwapChipsWithDifferentSlotTypesSocketClick')
SOCKET_ENTER_EVENT = Event('SwapChipsWithDifferentSlotTypesSocketEnter')

SOUND_CLICK = "SwapChipsWithDifferentSlotTypes_SlotClick"
SOUND_FAIL = "SwapChipsWithDifferentSlotTypes_FailClick"
SOUND_CANCEL = "SwapChipsWithDifferentSlotTypes_PutBack"
SOUND_SWAP = "SwapChipsWithDifferentSlotTypes_SwapChips"

CHIP_PLACED = 0
CHIP_NOT_PLACED = 1
CHIP_SELECTED = 2


class Slot(object):
    LAST_SLOT_ENTER = None

    @classmethod
    def setLastSlotEnter(cls, instance):
        cls.LAST_SLOT_ENTER = instance

    def __init__(self, slot_id, socket, slot, supported_chip_types, end_chip_ids, saved_slots_chip):
        self.id = slot_id

        self.socket = socket
        self.slot = slot

        self.supported_chip_types = supported_chip_types
        self.end_chip_ids = end_chip_ids

        self.chip = None  # Chip instance reference

        self.saved_slots_chip = saved_slots_chip  # save mg

        self.__tc_generate_event_click = None
        self.__tc_generate_event_enter = None

    def enableSocketEvents(self, b_enable):
        if b_enable:
            if self.socket is not None:
                self.__tc_generate_event_click = TaskManager.createTaskChain(Repeat=True)

                with self.__tc_generate_event_click as tc:
                    tc.addTask('TaskNodeSocketClick', isDown=True, Socket=self.socket)
                    tc.addFunction(SOCKET_CLICK_EVENT, self)

                self.__tc_generate_event_enter = TaskManager.createTaskChain(Repeat=True)

                with self.__tc_generate_event_enter as tc:
                    tc.addTask('TaskNodeSocketEnter', isMouseEnter=False, Socket=self.socket)
                    tc.addFunction(SOCKET_ENTER_EVENT, self)
                    tc.addFunction(self.setLastSlotEnter, self)

        else:
            if self.__tc_generate_event_click is not None:
                self.__tc_generate_event_click.cancel()
                self.__tc_generate_event_click = None

            if self.__tc_generate_event_enter is not None:
                self.__tc_generate_event_enter.cancel()
                self.__tc_generate_event_enter = None

    def isSupportChipType(self, slot):
        if slot is None:
            return False

        if self.supported_chip_types is None:
            return False

        if slot.chip is None:
            return True

        slot_chip_type = slot.chip.type

        return slot_chip_type in self.supported_chip_types

    def update(self):
        """if slot has chip: update it's current movie
        """

        if self.hasChip():
            if self.checkEndChip():
                self.chip.changeState(CHIP_PLACED)

            else:
                self.chip.changeState(CHIP_NOT_PLACED)

    def checkEndChip(self):
        if self.end_chip_ids is None:
            return False

        if not self.end_chip_ids:
            return True

        if self.chip is None:
            return False

        return self.chip.id in self.end_chip_ids

    def setChip(self, chip):
        if chip is not None:
            chip.slot = self  # save self reference to Chip instance

            self.chip = chip
            self.attachChip()

            self.saved_slots_chip[self.id] = chip.id  # save mg

    def getChip(self):
        if self.chip is not None:
            self.chip.detachFromParent()
            chip = self.chip
            self.chip = None

            self.saved_slots_chip[self.id] = None  # save mg

            return chip

    def hasChip(self):
        return self.chip is not None

    def attachChip(self):
        self.chip.attachToMovieSlot(self.slot)

    def destroy(self):
        self.enableSocketEvents(False)  # cancel task chains

        self.saved_slots_chip[self.id] = self.chip.id if self.chip is not None else None  # save mg


class Chip(object):
    def __init__(self, chip_id, type_, movie_not_placed, movie_placed, movie_selected, cb_make_movie):
        self.id = chip_id
        self.type = type_
        self.state = CHIP_NOT_PLACED

        self.slot = None  # # Slot instance reference

        self.movies = {
            CHIP_NOT_PLACED: cb_make_movie(movie_not_placed, Enable=True, Play=True, Loop=True),
            CHIP_PLACED: cb_make_movie(movie_placed, Enable=False, Play=True, Loop=True),
            CHIP_SELECTED: cb_make_movie(movie_selected, Enable=False, Play=True, Loop=True)
        }

        self.node = Mengine.createNode('Interender')

        for movie in self.movies.itervalues():
            if movie is not None:
                movie_entity_node = movie.getEntityNode()

                self.node.addChild(movie_entity_node)

        self.__tc_alpha_to = None

    def attachToMovieSlot(self, movie_slot):
        if movie_slot is not None:
            self.detachFromParent()

            movie_slot.addChild(self.node)

    def detachFromParent(self):
        if self.node.hasParent() is True:
            self.node.removeFromParent()

    def changeState(self, new_state, source=None, time_alpha=0.0, state_life_time=0.0):
        cur_movie = self.movies.get(self.state)
        new_movie = self.movies.get(new_state)

        self.state = new_state

        if not (cur_movie is None or new_movie is None):  # CHECK IF BOTH IS NOT NONE

            if self.__tc_alpha_to is not None:  # interrupt AlphaTo tc if exists
                self.__tc_alpha_to.cancel()
                self.__tc_alpha_to = None

            if time_alpha == 0.0:  # default case, no alpha transition

                cur_movie.setEnable(False)
                new_movie.setEnable(True)

            else:  # task chain case with alpha transition swap

                if source is None:  # create tc with source if no source passed
                    self.__tc_alpha_to = TaskManager.createTaskChain(AutoRun=False)
                    source = TaskSource(self.__tc_alpha_to.source)

                self.node.addChild(new_movie.entity.node)  # set this movie state on top of others
                new_movie.setEnable(True)

                source.addTask("TaskNodeAlphaTo", Node=new_movie.entity.node, From=0.0, To=1.0, Time=time_alpha)
                source.addDisable(cur_movie)

                if state_life_time != 0.0:
                    source.addDelay(state_life_time)
                    source.addEnable(cur_movie)
                    source.addTask("TaskNodeAlphaTo", Node=new_movie.entity.node, To=0.0, Time=time_alpha, IsTemp=True)
                    source.addDisable(new_movie)

                if self.__tc_alpha_to is not None:  # if tc with source was run task chain
                    self.__tc_alpha_to.run()

    def destroy(self):
        if self.__tc_alpha_to is not None:
            self.__tc_alpha_to.cancel()

        self.detachFromParent()

        for movie in self.movies.itervalues():
            movie.getEntityNode().removeFromParent()
            movie.onFinalize()
            movie.onDestroy()

        Mengine.destroyNode(self.node)
        self.node = None


class SwapChipsWithDifferentSlotTypes(Enigma):

    def __init__(self):
        super(SwapChipsWithDifferentSlotTypes, self).__init__()

        self.param = None

        self.movie_slots = None  # main MG Node

        self.slots = []  # Slots instances reference storage
        self.chips = []  # Chips instances reference storage

        self.fixed_slots_ids = []  # Store unmovable slot IDs
        self.allowed_slots_id = {}  # Store allowed slots IDs for each slot if MG DB for Slots has this params

        self.slots_to_lit = {}  # Store slots instances arrays by type key

        self.litted_chips_temp = []  # store litted chips to unlit them after

        self.slot_holder_1 = None  # hold slot click result
        self.slot_holder_2 = None  # hold slot click result

        self.__tc = None

    @staticmethod
    def declareORM(type_):
        Enigma.declareORM(type_)
        type_.addAction(type_, 'savedSlotChips')  # store chip/slot position for Save/Load MG

    # -------------- Main ----------------------------------------------------------------------------------------------
    def loadParam(self):
        self.param = SwapChipsWithDifferentSlotTypesManager.getParam(self.EnigmaName)

    def makeMovie(self, movie_name, **params):
        """ DEPRECATED way of movie 2 creation
        """

        if movie_name is not None:
            group_name = self.object.getGroupName()
            if group_name is not None:
                return Utils.makeMovie2(group_name, movie_name, **params)

    def setup(self, restore=False):
        """ Main MG constructor
        """

        movie_slots_name = self.param.getMovieSlotsName()
        self.movie_slots = self.object.getObject(movie_slots_name)

        slots_data = self.param.getSlots()
        chips_data = self.param.getChips()

        if self.param.FixedSlotsIDs is not None:
            self.fixed_slots_ids = self.param.FixedSlotsIDs

        for slot_id, slot_param in slots_data.iteritems():
            movie_slot = self.movie_slots.getMovieSlot(slot_param.MovieSlot)
            socket = self.movie_slots.getSocket(slot_param.MovieSocket)

            slot = Slot(slot_id, socket, movie_slot, slot_param.SupportedChipTypes, slot_param.EndChipIDs,
                        self.savedSlotChips)

            self.slots.append(slot)

            if restore is False:
                chip_id = slot_param.StartChipID

            else:
                chip_id = self.savedSlotChips[slot_id]

            self.allowed_slots_id[slot_id] = slot_param.AllowedSlots

            if chip_id is None:
                continue

            chip_param = chips_data.get(chip_id)
            if chip_param is None:
                continue

            chip = Chip(chip_id, chip_param.Type, chip_param.MovieNotPlaced, chip_param.MoviePlaced,
                        chip_param.MovieSelected, self.makeMovie)

            self.chips.append(chip)

            slot.setChip(chip)
            slot.update()  # chip initial movie state

        for slot in self.slots:
            temp_slots = list(self.slots)
            temp_slots.remove(slot)

            self.slots_to_lit[slot.id] = []

            for slot_to_swap in temp_slots:
                if slot_to_swap.id in self.fixed_slots_ids:
                    continue

                for chip_type in slot.supported_chip_types:
                    if chip_type in slot_to_swap.supported_chip_types:
                        self.slots_to_lit[slot.id].append(slot_to_swap)
                        break

    def cleanUp(self):
        if self.__tc is not None:
            self.__tc.cancel()
            self.__tc = None

        for slot in self.slots:
            slot.destroy()

        for chip in self.chips:
            chip.destroy()

        # reset mg containers
        self.slots = []
        self.chips = []
        self.fixed_slots_ids = []
        self.allowed_slots_id = {}
        self.litted_chips_temp = []
        self.slots_to_lit = {}

    #
    #
    #

    def playSound(self, sound):
        Notification.notify(Notificator.onSoundEffectOnObject, self.object, sound)  # print 'mg sound "%s"' % sound

    def litChips(self, b_lit, slot=None):
        """lit up friendly slots

        Case 1: lit allowed slots ids
        Case 2: lit supported chips by type
        """

        # print 'mg lit: %d' % b_lit

        if b_lit:  # LIT CHIPS

            allowed_slots_ids = self.allowed_slots_id[slot.id]

            if len(allowed_slots_ids) != 0:  # LIT CHIPS ON ALLOWED SLOTS

                for slot_id in allowed_slots_ids:
                    chip = self.slots[slot_id - 1].chip

                    if chip is not None:
                        chip.changeState(CHIP_SELECTED, time_alpha=self.param.LitAlpha, state_life_time=self.param.LitTime)

                        self.litted_chips_temp.append(chip)  # add to temp buffer to unlit on next click

            else:  # LIT CHIPS ON SUPPORTED SLOTS:

                for slot_to_lit in self.slots_to_lit[slot.id]:
                    chip = slot_to_lit.chip

                    if chip is not None and chip.type in slot.supported_chip_types and slot.chip.type in slot_to_lit.supported_chip_types:
                        slot_to_lit.chip.changeState(CHIP_SELECTED, time_alpha=self.param.LitAlpha, state_life_time=self.param.LitTime)
                        self.litted_chips_temp.append(slot_to_lit.chip)

        else:  # UNLIT CHIPS

            for chip in self.litted_chips_temp:
                chip.slot.update()

            self.litted_chips_temp = []  # clean temp buffer

    def checkComplete(self):
        """If all chips in end position -> enigma complete
        """

        for slot in self.slots:
            if slot.checkEndChip() is False:
                break

        else:  # this is correct, google it
            self.enigmaComplete()

    def __scopeSetButton1(self, source):
        """Set first Holder of class Slot instances
        """

        def cbSetButtonSlot1(delegated_slot):
            self.slot_holder_1.set(delegated_slot)

            # print 'slot_holder_1.set(%s)' % delegated_slot.id

            return True

        source.addEvent(SOCKET_CLICK_EVENT, cbSetButtonSlot1)

    def __scopeSetButton2(self, source):
        """Set second Holder of class Slot instances
        !!! used only when drag drop mg control type
        """

        source.addFunction(self.slot_holder_2.set, Slot.LAST_SLOT_ENTER)

        # print 'slot_holder_2.set(%s)' % Slot.LAST_SLOT_ENTER.id

    # -------------- METHODS FOR DRAG DROP GAME CONTROL RULE -----------------------------------------------------------
    def __scopeActionMoveDragDrop(self, source):
        """Main Game Action, move chip too empty slot
        """

        slot_1 = self.slot_holder_1.get()
        chip_1 = slot_1.chip
        node_1 = slot_1.chip.node
        pos_node_1 = node_1.getWorldPosition()

        slot_2 = self.slot_holder_2.get()
        pos_slot_2 = slot_2.slot.getWorldPosition()

        if self.param.LitChips:
            self.litChips(False)

        source.addTask("TaskNodeMoveTo", Node=node_1, From=pos_node_1, To=pos_slot_2, Time=self.param.ChipMoveTime)
        source.addFunction(chip_1.changeState, CHIP_NOT_PLACED)
        source.addFunction(self.playSound, SOUND_CANCEL)

        source.addFunction(node_1.setLocalPosition, (0.0, 0.0))
        source.addFunction(slot_1.getChip)

        source.addFunction(slot_2.setChip, chip_1)
        source.addFunction(slot_2.update)

    def __scopeActionBackDragDrop(self, source, sound=None):
        """Main Game Action, put chip back to it slot
        """

        slot = self.slot_holder_1.get()
        chip_node = slot.chip.node

        pos_node = chip_node.getWorldPosition()
        pos_slot = slot.slot.getWorldPosition()

        if self.param.LitChips:
            self.litChips(False)

        if sound is not None:
            self.playSound(sound)

        source.addTask("TaskNodeMoveTo", Node=chip_node, From=pos_node, To=pos_slot, Time=self.param.ChipMoveTime)
        source.addFunction(slot.update)

    def __scopeActionSwapDragDrop(self, source):
        """Main Game Action, swap both chips
        """

        slot_1 = self.slot_holder_1.get()
        chip_1 = slot_1.chip
        node_1 = chip_1.node
        pos_node_1 = node_1.getWorldPosition()
        pos_slot_1 = slot_1.slot.getWorldPosition()

        slot_2 = self.slot_holder_2.get()
        chip_2 = slot_2.chip
        node_2 = chip_2.node
        pos_slot_2 = slot_2.slot.getWorldPosition()

        self.addChild(node_2)

        if self.param.LitChips:
            self.litChips(False)

        chip_2.changeState(CHIP_SELECTED)

        self.playSound(SOUND_CLICK)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskNodeMoveTo", Node=node_1, From=pos_node_1, To=pos_slot_2, Time=self.param.ChipMoveTime)
            parallel_0.addFunction(chip_1.changeState, CHIP_NOT_PLACED)

            parallel_1.addTask("TaskNodeMoveTo", Node=node_2, From=pos_slot_2, To=pos_slot_1, Time=self.param.ChipMoveTime)
            parallel_1.addFunction(chip_2.changeState, CHIP_NOT_PLACED)

        source.addFunction(self.playSound, SOUND_SWAP)

        source.addFunction(node_1.setLocalPosition, (0.0, 0.0))
        source.addFunction(node_2.setLocalPosition, (0.0, 0.0))

        source.addFunction(slot_1.getChip)
        source.addFunction(slot_2.getChip)

        source.addFunction(slot_1.setChip, chip_2)
        source.addFunction(slot_2.setChip, chip_1)

        source.addFunction(slot_1.update)
        source.addFunction(slot_2.update)

    def __validationCanSwapDragDrop(self):
        slot_1 = self.slot_holder_1.get()
        slot_2 = self.slot_holder_2.get()
        allowed_slots = self.allowed_slots_id[slot_1.id]

        if slot_1 is None:
            return False

        if slot_2.id in self.fixed_slots_ids:
            return False

        if slot_1.isSupportChipType(slot_2) is False:
            return False

        if slot_2.isSupportChipType(slot_1) is False:
            return False

        if len(allowed_slots) != 0:
            if slot_2.id not in allowed_slots:
                return False

        return True

    def __validationCanMoveDragDrop(self):
        slot_1 = self.slot_holder_1.get()

        if slot_1.hasChip() is False:
            return False

        if slot_1.id in self.fixed_slots_ids:
            return False

        return True

    def __scopeSwitchActionDragDrop(self, source):
        """Resolve switch main action
        """

        slot_1 = self.slot_holder_1.get()
        slot_2 = self.slot_holder_2.get()

        if self.__validationCanSwapDragDrop() is False:
            source.addScope(self.__scopeActionBackDragDrop, sound=SOUND_FAIL)
            return

        if slot_1 == slot_2:
            source.addScope(self.__scopeActionBackDragDrop, sound=SOUND_CANCEL)

        elif slot_2.hasChip() is True:
            if self.param.PlaySwapSoundTwice:
                self.playSound(SOUND_SWAP)

            source.addScope(self.__scopeActionSwapDragDrop)

        else:
            source.addScope(self.__scopeActionMoveDragDrop)

    def __scopeToCursorDragDrop(self, source):
        """Move chip on cursor position using TC
        """

        slot_1 = self.slot_holder_1.get()
        chip_1 = slot_1.chip
        node_1 = chip_1.node
        self.addChild(node_1)

        pos_node_1 = node_1.getWorldPosition()
        pos_cursor = Mengine.getCursorPosition()

        source.addTask("TaskNodeMoveTo", Node=node_1, From=pos_node_1, To=pos_cursor)

    def __scopeToCursorUntilMouseUpDragDrop(self, source):
        """Move chip on cursor position loop
        """

        slot_1 = self.slot_holder_1.get()
        slot_1.chip.changeState(CHIP_SELECTED)

        self.playSound(SOUND_CLICK)

        if self.param.LitChips:
            self.litChips(True, slot_1)

        with source.addRepeatTask() as (repeat, until):
            repeat.addScope(self.__scopeToCursorDragDrop)

            until.addTask("TaskMouseButtonClick", isDown=False)

    # -------------- METHODS FOR CLICK ON BOTH CHIPS GAME CONTROL RULE -------------------------------------------------
    def __scopeActionMoveOnClick(self, source, slot_1, slot_2):
        """Main Game Action, Move chip on empty slot
        """

        from_slot = slot_1 if slot_2.hasChip() is False else slot_2
        to_slot = slot_1 if slot_2.hasChip() is True else slot_2

        chip_1 = from_slot.chip
        node_chip_1 = chip_1.node
        pos_node_1 = node_chip_1.getWorldPosition()
        pos_slot_2 = to_slot.slot.getWorldPosition()

        self.addChild(node_chip_1)

        self.playSound(SOUND_CANCEL)

        source.addTask("TaskNodeMoveTo", Node=node_chip_1, From=pos_node_1, To=pos_slot_2, Time=self.param.ChipMoveTime)

        source.addFunction(node_chip_1.setLocalPosition, (0.0, 0.0))

        source.addFunction(from_slot.getChip)

        source.addFunction(to_slot.setChip, chip_1)
        source.addFunction(to_slot.update)

    def __scopeActionSwapOnClick(self, source, slot_1, slot_2):
        """Main Game Action, swap both chips
        """

        chip_1 = slot_1.chip
        chip_2 = slot_2.chip

        node_1 = chip_1.node
        node_2 = chip_2.node

        pos_node_1 = node_1.getWorldPosition()
        pos_node_2 = node_2.getWorldPosition()

        self.addChild(node_1)
        self.addChild(node_2)

        self.playSound(SOUND_CLICK)

        chip_1.changeState(CHIP_SELECTED)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskNodeMoveTo", Node=node_1, From=pos_node_1, To=pos_node_2, Time=self.param.ChipMoveTime)

            parallel_1.addTask("TaskNodeMoveTo", Node=node_2, From=pos_node_2, To=pos_node_1, Time=self.param.ChipMoveTime)

        source.addFunction(self.playSound, SOUND_SWAP)

        source.addFunction(node_1.setLocalPosition, (0.0, 0.0))
        source.addFunction(node_2.setLocalPosition, (0.0, 0.0))

        source.addFunction(slot_1.getChip)
        source.addFunction(slot_2.getChip)

        source.addFunction(slot_1.setChip, chip_2)
        source.addFunction(slot_2.setChip, chip_1)

        source.addFunction(slot_1.update)
        source.addFunction(slot_2.update)

    def __scopeSwitchActionOnClick(self, source):
        """Resolve Chip Click: fail, cancel, first chip clicked, second chip clicked

        slot_holder_1 always contain current clicked slot
        slot_holder_2 can or can not contain previous clicked slot
        """
        slot_1 = self.slot_holder_1.get()  # current clicked slot
        slot_2 = self.slot_holder_2.get()  # previous clicked slot

        # CASE CANCEL
        if slot_1 is None or (slot_1 is slot_2):
            if slot_1 is None:  # possible only when we clicked "back" socket

                if slot_2 is None:  # possible only when we clicked twice socket "back"
                    return

                slot_1 = slot_2

            # print 'mg cancel click slot(id="%s")' % slot_1.id

            self.playSound(SOUND_CANCEL)

            self.slot_holder_2.set(None)  # drop previous clicked slot

            slot_1.update()

            if self.param.LitChips:
                self.litChips(False)

        # CASE FAIL     # fixme: strange ifs
        elif slot_1.id in self.fixed_slots_ids:
            self._caseFail(slot_1, slot_2)
        elif slot_2 is None and not slot_1.hasChip():
            self._caseFail(slot_1, slot_2)
        elif (slot_2 is not None and slot_2 is not slot_1 and ((not slot_1.isSupportChipType(slot_2) or not slot_2.isSupportChipType(slot_1)) or (bool(self.allowed_slots_id[slot_1.id]) and slot_2.id not in self.allowed_slots_id[slot_1.id]))):
            self._caseFail(slot_1, slot_2)

        # CASE CLICK FIRST
        elif slot_2 is None:
            # print 'mg click first slot(id="%s")' % slot_1.id

            self.playSound(SOUND_CLICK)

            self.slot_holder_2.set(slot_1)  # mark current slot as previous

            slot_1.chip.changeState(CHIP_SELECTED)

            if self.param.LitChips:
                self.litChips(True, slot=slot_1)

        # CASE CLICK SECOND
        else:
            # print 'mg click second slot(id="%s")' % slot_1.id

            self.slot_holder_2.set(None)

            if self.param.LitChips:
                self.litChips(False)

            if slot_1.hasChip() is True:
                if self.param.PlaySwapSoundTwice:
                    self.playSound(SOUND_SWAP)

                source.addScope(self.__scopeActionSwapOnClick, slot_1, slot_2)  # MAIN ACTION SWAP

            else:
                source.addScope(self.__scopeActionMoveOnClick, slot_1, slot_2)  # MAIN ACTION MOVE

    def _caseFail(self, slot_1, slot_2):
        # print 'mg fail click slot "is fixed" OR "empty" OR "not supported chip type" OR "not in allowed_slots'

        self.playSound(SOUND_FAIL)
        self.slot_holder_2.set(None)

        slot_1.update()
        if slot_2 is not None:
            slot_2.update()

        if self.param.LitChips:
            self.litChips(False)

    # -------------- TaskChain -----------------------------------------------------------------------------------------
    def runTaskChain(self):
        """Run Game Logic
        """

        for slot in self.slots:
            slot.enableSocketEvents(True)

        self.slot_holder_1 = Holder()
        self.slot_holder_2 = Holder()

        self.__tc = TaskManager.createTaskChain(Repeat=True)
        with self.__tc as tc:
            tc.addFunction(self.checkComplete)

            if self.param.DragDrop:
                # RUN TASK CHAIN WITH DRAG DROP CONTROL RULE

                tc.addScope(self.__scopeSetButton1)

                with tc.addIfTask(self.__validationCanMoveDragDrop) as (true, false):
                    true.addScope(self.__scopeToCursorUntilMouseUpDragDrop)

                    true.addScope(self.__scopeSetButton2)
                    true.addScope(self.__scopeSwitchActionDragDrop)

                    false.addFunction(self.playSound, SOUND_FAIL)

            else:
                # RUN TASK CHAIN WITH DOUBLE CLICK GAME CONTROL RULE

                with tc.addRaceTask(2) as (race_0, race_1):
                    race_0.addScope(self.__scopeSetButton1)

                    if self.movie_slots.hasSocket('back'):  # deselect on back click
                        race_1.addTask('TaskMovie2SocketClick', SocketName='back', Movie2=self.movie_slots)
                        race_1.addFunction(self.slot_holder_1.set, None)
                    else:
                        race_1.addBlock()

                tc.addScope(self.__scopeSwitchActionOnClick)

    # -------------- BaseEntity ----------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(SwapChipsWithDifferentSlotTypes, self)._onPreparation()
        self.loadParam()

        # Resolve Save/Load on manager param
        if self.Playing is False:
            self.setup()
        else:
            self.setup(restore=self.param.SaveMG)

    def _onActivate(self):
        super(SwapChipsWithDifferentSlotTypes, self)._onActivate()

    def _onDeactivate(self):
        super(SwapChipsWithDifferentSlotTypes, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma  -------------------------------------------------------------------------------------------
    def _playEnigma(self):  # on first run
        self.runTaskChain()

    def _stopEnigma(self):  # when exit and complete
        if self.__tc is not None:
            self.__tc.cancel()

    def _restoreEnigma(self):  # when not first run
        self.runTaskChain()

    def _resetEnigma(self):  # when reset button activated
        self.cleanUp()
        self.setup()
        self.runTaskChain()

    def _skipEnigmaScope(self, source):  # when skip button activated
        if self.param.PlaySkip:
            if self.__tc is not None:
                self.__tc.cancel()

            for slot in self.slots:
                slot.chip = None

            for chip, parallel in source.addParallelTaskList(self.chips):
                for slot in self.slots:
                    if slot.chip is None and chip.id in slot.end_chip_ids and chip.node is not None and slot.slot is not None:
                        slot.chip = chip

                        parallel.addFunction(self.addChild, chip.node)

                        parallel.addFunction(chip.changeState, CHIP_SELECTED)
                        parallel.addTask("TaskNodeMoveTo", Node=chip.node, From=chip.node.getWorldPosition(),
                                         To=slot.slot.getWorldPosition(), Time=self.param.ChipMoveTime)

                        parallel.addFunction(chip.node.setLocalPosition, (0.0, 0.0))
                        parallel.addFunction(chip.detachFromParent)
                        parallel.addFunction(chip.attachToMovieSlot, slot.slot)
                        parallel.addFunction(chip.changeState, CHIP_PLACED)
