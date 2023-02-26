from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.SwapAndRotateMovieChipsManager import SwapAndRotateMovieChipsManager

Enigma = Mengine.importEntity("Enigma")

class SwapAndRotateMovieChips(Enigma):
    # - Service classes ----------------------------------------------
    class Slot(object):
        def __init__(self, SlotID, Socket, Slot, EndChipID, EndChipRotation, EndChipID2, EndChipRotation2):
            self.id = SlotID

            self.socket = Socket
            self.slot = Slot

            self.end_chip_id = EndChipID
            self.end_chip_rotation = EndChipRotation

            # Extra variant
            self.end_chip_id2 = EndChipID2
            self.end_chip_rotation2 = EndChipRotation2

            self.chip = None

        def setRotation(self, Rotation):
            if Rotation is None:
                return

            self.rotation = Rotation

        def getID(self):
            return self.id

        def clickScope(self, source):
            if self.socket is None:
                return
            source.addTask('TaskNodeSocketClick', Socket=self.socket)  # source.addPrint(" = Click on Slot with ID=%s with chip ID=%s", self.id, self.chip.getID())

        def checkEndChip(self):
            if self.chip is None:
                return False

            if self.end_chip_id is None:
                return False

            b_chip_in_end = self.chip.getID() == self.end_chip_id
            b_rotations = self.chip.checkRotations(self.end_chip_rotation) is True

            if b_chip_in_end is False or b_rotations is False:
                b_chip_in_end = self.chip.getID() == self.end_chip_id2
                b_rotations = self.chip.checkRotations(self.end_chip_rotation2) is True

            return b_chip_in_end and b_rotations

        def setChip(self, Chip):
            if Chip is None:
                return

            self.chip = Chip

            self.attachChip()

        def getChip(self):
            if self.chip is None:
                return None

            self.chip.detachFromParent()

            chip = self.chip
            self.chip = None

            return chip

        def attachChip(self):
            self.chip.attachToMovieSlot(self.slot)

        def destroy(self):
            chip = self.getChip()
            chip.destroy()

            self.id = None
            self.socket = None
            self.slot = None
            self.chip = None

    class Chip(object):
        def __init__(self, ChipID, MovieIdle, MovieSelected, MakeMovieFunc, RotationAngle, RotationCount):
            self.id = ChipID

            self.state = None

            self.rotation_angle = RotationAngle
            self.rotation_count = RotationCount

            self.rotation = 0

            self.rotation_time = 200  # ms

            self.movies = dict(Idle=MakeMovieFunc(MovieIdle, Enable=False, Play=True, Loop=True), Selected=MakeMovieFunc(MovieSelected, Enable=False, Play=True, Loop=True), )

            self.node = Mengine.createNode('Interender')

            for movie in self.movies.itervalues():
                if movie is None:
                    continue

                movie_entity_node = movie.getEntityNode()
                self.node.addChild(movie_entity_node)

        def calcRotationAngle(self):
            return self.rotation * self.rotation_angle

        def setRotation(self, rotation):
            self.rotation = rotation

            angle = self.calcRotationAngle()
            self.node.setAngle(angle)

        def checkRotation(self, rotation):
            chip_rotation = self.rotation % self.rotation_count
            return chip_rotation is rotation

        def checkRotations(self, *rotations):
            for rotation in rotations:
                if self.checkRotation(rotation) is True:
                    return True
            return False

        def getID(self):
            return self.id

        def getNode(self):
            return self.node

        def attachToMovieSlot(self, MovieSlot):
            if MovieSlot is None:
                return

            self.detachFromParent()

            MovieSlot.addChild(self.node)

        def detachFromParent(self):
            if self.node.hasParent() is True:
                self.node.removeFromParent()

        def changeState(self, NewState):
            if NewState is None:
                return

            if self.state == NewState:
                return

            CurStateMovie = self.movies.get(self.state)
            if CurStateMovie is not None:
                CurStateMovie.setEnable(False)

            NewStateMovie = self.movies.get(NewState)
            if NewStateMovie is None:
                return

            NewStateMovie.setEnable(True)

            self.state = NewState

        def rotateScope(self, source):
            self.rotation += 1
            AngleTo = self.calcRotationAngle()

            source.addTask('TaskNodeRotateTo', Node=self.node, Time=self.rotation_time, To=AngleTo)

        def destroy(self):
            self.detachFromParent()

            for movie in self.movies.itervalues():
                movie_entity_node = movie.getEntityNode()
                movie_entity_node.removeFromParent()
                movie.onFinalize()
                movie.onDestroy()

            self.movies = {}

            Mengine.destroyNode(self.node)
            self.node = None

            self.state = None

    # ----------------------------------------------------------------

    def __init__(self):
        super(SwapAndRotateMovieChips, self).__init__()

        self.param = None

        self.MovieSlots = None
        self.Button_Rotate = None

        self.slots = []

        self.tc = None

    def load_param(self):
        self.param = SwapAndRotateMovieChipsManager.getParam(self.EnigmaName)

    def setup(self):
        if self.slots:
            return

        if self.param is None:
            msg = "Enigma {}: self.param is None on setup stage".format(self.EnigmaName)
            Trace.log("Entity", 0, msg)
            return

        MovieSlotsName = self.param.getMovieSlotsName()
        if MovieSlotsName is None:
            msg = "Enigma {}: MovieSlotsName in Param is None".format(self.EnigmaName)
            Trace.log("Entity", 0, msg)
            return

        self.Button_Rotate = self.object.getObject(self.param.RotationButton)
        self.Button_Rotate.setParam("Block", True)

        self.MovieSlots = self.object.getObject(MovieSlotsName)
        if self.MovieSlots is None:
            return

        slots_data = self.param.getSlots()
        chips_data = self.param.getChips()

        for slot_id, slot_param in slots_data.iteritems():
            MovieSlot = self.MovieSlots.getMovieSlot(slot_param.MovieSlot)
            Socket = self.MovieSlots.getSocket(slot_param.MovieSocket)

            slot = SwapAndRotateMovieChips.Slot(slot_id, Socket, MovieSlot, slot_param.EndChipID, slot_param.EndChipRotation, slot_param.EndChipID2, slot_param.EndChipRotation2)

            self.slots.append(slot)

            chip_id = slot_param.StartChipID

            if chip_id is None:
                continue

            chip_param = chips_data.get(chip_id)

            if chip_param is None:
                continue

            RotationAngle = self.param.getRotationAngle()

            chip = SwapAndRotateMovieChips.Chip(chip_id, chip_param.MovieIdle, chip_param.MovieSelected, self._makeMovie, RotationAngle, self.param.RotationCount)

            chip.setRotation(slot_param.StartChipRotation)

            slot.setChip(chip)

            slot.chip.changeState('Idle')
        pass

    def _makeMovie(self, MovieName, **Params):
        if MovieName is None:
            return None

        GroupName = self.object.getGroupName()
        if GroupName is None:
            return None

        Movie = Utils.makeMovie2(GroupName, MovieName, **Params)

        return Movie

    def _onPreparation(self):
        super(SwapAndRotateMovieChips, self)._onPreparation()
        self.preparation()
        pass

    def preparation(self):
        self.load_param()
        self.setup()

    def _playEnigma(self):
        self.runTaskChain()

    def runTaskChain(self):
        CurClickSlotHolder = Holder()
        PrevClickSlotHolder = Holder()

        StateHolder = Holder()

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.updateSlotsScope, CurClickSlotHolder, PrevClickSlotHolder)
            tc.addFunction(self.checkComplete)

            with tc.addRaceTask(3) as (tc_rotation, tc_slots, tc_back):
                tc_rotation.addScope(self.rotationClickScope)
                tc_rotation.addFunction(StateHolder.set, 'rotation')

                for slot, tc_race in tc_slots.addRaceTaskList(self.slots):
                    tc_race.addScope(slot.clickScope)
                    tc_race.addFunction(CurClickSlotHolder.set, slot)

                tc_slots.addFunction(StateHolder.set, 'slots')

                tc_back.addScope(self.backClickScope)
                tc_back.addFunction(StateHolder.set, 'back')

            tc.addScope(self.resolveStateScope, StateHolder, CurClickSlotHolder, PrevClickSlotHolder)

    def resolveStateScope(self, source, StateHolder, CurClickSlotHolder, PrevClickSlotHolder):
        state = StateHolder.get()

        if state == 'rotation':
            source.addScope(self.resolveRotationScope, CurClickSlotHolder)
        elif state == 'slots':
            source.addScope(self.resolveClickScope, CurClickSlotHolder, PrevClickSlotHolder)
        elif state == 'back':
            source.addFunction(CurClickSlotHolder.set, None)
            source.addFunction(PrevClickSlotHolder.set, None)

        StateHolder.set(None)

    def backClickScope(self, source):
        if self.MovieSlots.hasSocket('back') is False:
            source.addBlock()
            return

        source.addTask('TaskMovie2SocketClick', SocketName='back', Movie2=self.MovieSlots)

    def resolveRotationScope(self, source, CurClickSlotHolder):
        CurClickSlot = CurClickSlotHolder.get()

        if CurClickSlot is None:
            # source.addPrint(" =========== ROTATION: Nothing to Rotate =============")
            return

        # source.addPrint(" ================= LETS ROTATE CHIP ON SLOT %s ==============", CurClickSlot.getID())
        with source.addParallelTask(2) as (Rotate, SoundEffect):
            SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateMovieChips_RotateChip')
            Rotate.addScope(CurClickSlot.chip.rotateScope)

    def rotationClickScope(self, source):
        if self.param.RotationButton is None:
            source.addBlock()
            return

        # if self.MovieSlots.hasSocket(self.param.RotationSocket) is False:
        #     source.addBlock()
        #     return

        # source.addTask('TaskMovieSocketClick', SocketName=self.param.RotationButton, Movie=self.MovieSlots)

        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.Button_Rotate)

    def resolveClickScope(self, source, CurClickSlotHolder, PrevClickSlotHolder):
        CurClickSlot = CurClickSlotHolder.get()
        PrevClickSlot = PrevClickSlotHolder.get()

        source.addFunction(CurClickSlot.chip.changeState, 'Selected')

        if PrevClickSlot is None:
            with source.addParallelTask(2) as (Select, SoundEffect):
                Select.addFunction(self.Button_Rotate.setParam, "Block", False)
                Select.addFunction(PrevClickSlotHolder.set, CurClickSlot)
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateMovieChips_SelectChip')
            return

        CurClickSlotHolder.set(None)
        PrevClickSlotHolder.set(None)

        if CurClickSlot == PrevClickSlot:
            with source.addParallelTask(2) as (Deselect, SoundEffect):
                Deselect.addFunction(CurClickSlot.chip.changeState, 'Idle')
                Deselect.addFunction(self.Button_Rotate.setParam, "Block", True)
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateMovieChips_SelectChip')
            return
        with source.addParallelTask(2) as (Swap, SoundEffect):
            Swap.addScope(self.swapChipsScope, CurClickSlot, PrevClickSlot)
            SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateMovieChips_SwapChips')

            source.addFunction(self.Button_Rotate.setParam, "Block", True)

    def swapChipsScope(self, source, FirstSlot, SecondSlot):
        # source.addPrint("dummy swap scope slot1=%s slot2=%s", FirstSlot.getID(), SecondSlot.getID())

        first_chip = FirstSlot.chip
        second_chip = SecondSlot.chip

        first_node = first_chip.getNode()
        second_node = second_chip.getNode()

        first_pos = first_node.getWorldPosition()
        second_pos = second_node.getWorldPosition()

        self.addChild(first_node)
        self.addChild(second_node)

        DefaultSwapTime = DefaultManager.getDefaultFloat('SwapChipsWithDifferentSlotTypesTime', 400.0)

        with source.addParallelTask(2) as (tc_first_node, tc_second_node):
            tc_first_node.addTask("TaskNodeMoveTo", Node=first_node, From=first_pos, To=second_pos, Time=DefaultSwapTime)
            tc_second_node.addTask("TaskNodeMoveTo", Node=second_node, From=second_pos, To=first_pos, Time=DefaultSwapTime)

        source.addFunction(first_node.setLocalPosition, (0.0, 0.0))
        source.addFunction(second_node.setLocalPosition, (0.0, 0.0))

        source.addFunction(FirstSlot.getChip)
        source.addFunction(SecondSlot.getChip)

        source.addFunction(FirstSlot.setChip, second_chip)
        source.addFunction(SecondSlot.setChip, first_chip)
        pass

    def updateSlotsScope(self, source, CurClickSlotHolder, PrevClickSlotHolder):
        cur_slot = CurClickSlotHolder.get()
        prev_slot = PrevClickSlotHolder.get()

        for slot in self.slots:
            if slot is None:
                continue

            if slot is cur_slot:
                continue

            if slot is prev_slot:
                continue

            slot.chip.changeState('Idle')
        pass

    def checkComplete(self):
        for slot in self.slots:
            if slot.checkEndChip() is False:
                break
        else:
            self.enigmaComplete()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._clean_resources()
        self.preparation()
        self._playEnigma()

    def _clean_resources(self):
        if self.tc is not None:
            self.tc.cancel()

        self.tc = None

        for slot in self.slots:
            slot.destroy()

        self.slots = []

        self.param = None
        self.MovieSlots = None

    def _onDeactivate(self):
        super(SwapAndRotateMovieChips, self)._onDeactivate()
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None  # print "Enigma _onDeactivate ", self.EnigmaName

    def _onFinalize(self):
        super(SwapAndRotateMovieChips, self)._onFinalize()
        # print "Enigma _onFinalize ", self.EnigmaName

        self._clean_resources()