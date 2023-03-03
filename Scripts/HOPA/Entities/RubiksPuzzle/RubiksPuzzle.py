from Foundation.TaskManager import TaskManager
from HOPA.RubiksPuzzleManager import RubiksPuzzleManager


Enigma = Mengine.importEntity("Enigma")


class RubiksPuzzle(Enigma):
    class PuzzleSlot(object):
        def __init__(self, slot):
            self.slot = slot
            self.movie = None

        def getSlotName(self):
            return self.slot.getName()

        def getMovieSlot(self):
            return self.slot

        def attachMovie(self, movie):
            self.setMovie(movie)

            if self.movie is None:
                return

            movie_entity_node = self.movie.getEntityNode()

            self.slot.addChild(movie_entity_node)

            movie_entity_node.setLocalPosition((0.0, 0.0))

        def detachMovie(self):
            if self.movie is None:
                return None

            movie = self.movie
            self.movie = None

            movie_entity_node = movie.getEntityNode()
            movie_entity_node.removeFromParent()

            return movie

        def setMovie(self, movie):
            if self.slot is None:
                return

            if movie is None:
                return

            self.movie = movie

        def scopeClick(self, source):
            if self.movie is None:
                source.addBlock()
                return

            source.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName="socket")

        def scopeMoveMovieToSlotUsingEntity(self, source, slot, entity):
            if self.movie is None:
                source.addBlock()
                return

            movie_entity_node = self.movie.getEntityNode()
            movie_slot_to = slot.getMovieSlot()

            current_pos = movie_entity_node.getWorldPosition()
            slot_to_pos = movie_slot_to.getWorldPosition()

            entity_pos = entity.object.getPosition()

            from_pos = current_pos.x - entity_pos[0], current_pos.y - entity_pos[1]
            position_to = slot_to_pos.x - entity_pos[0], slot_to_pos.y - entity_pos[1]

            speed = 500.0

            movie = self.detachMovie()

            entity.addChild(movie_entity_node)

            source.addTask("TaskNodeMoveTo", Node=movie_entity_node, From=from_pos, To=position_to, Speed=speed)
            source.addFunction(slot.attachMovie, movie)

    def __init__(self):
        super(RubiksPuzzle, self).__init__()

        self.param = None
        self.slots_state = {}

        self.puzzle_slots = {}

    def load_data(self):
        self.param = RubiksPuzzleManager.getParam(self.EnigmaName)

    def setup(self):
        self.slots_state = self.param.getStartState().copy()
        self.create_slots()

    def create_slots(self):
        MovieSlotsName = self.param.getMovieSlotsName()
        PrototypeMovieChip1, PrototypeMovieChip2 = self.param.getPrototypeMovieChip1(), self.param.getPrototypeMovieChip2()

        MovieSlots = self.object.getObject(MovieSlotsName)

        for slot_name, state in self.slots_state.iteritems():
            puzzle_slot = MovieSlots.getMovieSlot(slot_name)

            MovieName = "Movie2_" + slot_name
            Params = dict(Enable=True, Loop=True, Play=True)

            Movie = None

            if state is 1:
                Movie = self.object.generateObject(MovieName, PrototypeMovieChip1, Params)
            elif state is 2:
                Movie = self.object.generateObject(MovieName, PrototypeMovieChip2, Params)

            puzzle_slot = RubiksPuzzle.PuzzleSlot(puzzle_slot)
            puzzle_slot.attachMovie(Movie)
            self.puzzle_slots[slot_name] = puzzle_slot

    def destroy_slots(self):
        for slot in self.puzzle_slots.itervalues():
            Movie = slot.detachMovie()

            self.object.removeObject(Movie)

            Movie.onDeactivate()
            Movie.onFinalize()
            Movie.onDestroy()

    def detach_from_slots(self):
        for slot in self.puzzle_slots.itervalues():
            Movie = slot.detachMovie()

            if Movie is None:
                continue

            self.object.removeObject(Movie.getName())

            Movie.onDeactivate()
            Movie.onFinalize()
            Movie.onDestroy()

    def findSlotToMove(self, puzzle_slot):
        vertex_name = puzzle_slot.getSlotName()

        adjacent_vertices = self.param.getAdjacentVerticesForVertex(vertex_name)

        for adjacent_vertex in adjacent_vertices:
            state = self.slots_state[adjacent_vertex]
            if state is 0:
                return self.puzzle_slots[adjacent_vertex]

        return None

    def scopeClick(self, source, holder):
        for (slot_name, puzzle_slot), tc_race in source.addRaceTaskList(self.puzzle_slots.iteritems()):
            tc_race.addScope(puzzle_slot.scopeClick)
            tc_race.addFunction(holder.set, puzzle_slot)

    def scopeMoveTo(self, source, holder_click, holder_move_to):
        puzzle_slot_click = holder_click.get()
        puzzle_slot_move_to = holder_move_to.get()

        puzzle_slot_click_name = puzzle_slot_click.getSlotName()
        puzzle_slot_move_to_name = puzzle_slot_move_to.getSlotName()

        self.slots_state[puzzle_slot_move_to_name], self.slots_state[puzzle_slot_click_name] = \
            self.slots_state[puzzle_slot_click_name], self.slots_state[puzzle_slot_move_to_name]

        source.addScope(puzzle_slot_click.scopeMoveMovieToSlotUsingEntity, puzzle_slot_move_to, self)

    def canBeMoved(self, holder_click, holder_move_to):
        puzzle_slot_click = holder_click.get()

        puzzle_slot_move_to = self.findSlotToMove(puzzle_slot_click)

        if puzzle_slot_move_to is None:
            return False

        holder_move_to.set(puzzle_slot_move_to)
        return True

    def _onPreparation(self):
        super(RubiksPuzzle, self)._onPreparation()
        self.preparation()
        pass

    def preparation(self):
        self.load_data()
        self.setup()

    def _playEnigma(self):
        # self.load_data()
        # self.setup()

        ClickSlotHolder = Holder()
        MoveToSlotHolder = Holder()

        with TaskManager.createTaskChain(Name="RubiksPuzzle", Repeat=True) as tc:
            tc.addScope(self.scopeClick, ClickSlotHolder)

            with tc.addIfTask(self.canBeMoved, ClickSlotHolder, MoveToSlotHolder) as (tc_can_move, tc_cant_move):
                with tc_can_move.addParallelTask(2) as (Move, SoundEffect):
                    Move.addScope(self.scopeMoveTo, ClickSlotHolder, MoveToSlotHolder)
                    SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'RubiksPuzzle_Move')

            tc.addFunction(self._check_complete)

    def _check_complete(self):
        if self.param.isWinState(self.slots_state) is True:
            self.enigmaComplete()

    def _stopEnigma(self):
        pass

    def _pauseEnigma(self):
        self._stopEnigma()

    def _resetEnigma(self):
        self._clean_resources()
        self.load_data()
        self.setup()
        self._playEnigma()
        pass

    def _clean_resources(self):
        TaskManager.cancelTaskChain("RubiksPuzzle", exist=False)

        self.detach_from_slots()

        self.param = None
        self.slots_state = {}
        self.puzzle_slots = {}

    def _onDeactivate(self):
        super(RubiksPuzzle, self)._onDeactivate()  # self._clean_resources()

    def _onFinalize(self):
        super(RubiksPuzzle, self)._onFinalize()

        self._clean_resources()

    def _restoreEnigma(self):
        self._playEnigma()
