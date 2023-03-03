from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager
from HOPA.ChipMoveAtomManager import ChipMoveAtomManager


Enigma = Mengine.importEntity("Enigma")


class ChipMoveAtom(Enigma):
    # - Service classes -----------------------------------------------------------------------------------------------
    class Base(object):
        def __init__(self):
            self.node = Mengine.createNode('Interender')
            self.movies = {}

        def _attach_movie(self, name, movie):
            if name in self.movies:
                return

            if movie is None:
                return

            movie_entity_node = movie.getEntityNode()
            self.node.addChild(movie_entity_node)

            self.movies[name] = movie

        def get_node(self):
            return self.node

        def clean(self):
            for movie in self.movies.itervalues():
                movie.onDestroy()
            self.movies = {}

            if self.node is not None:
                Mengine.destroyNode(self.node)
                self.node = None

    class Chip(Base):
        def __init__(self, chip_movie, glow_movie):
            super(ChipMoveAtom.Chip, self).__init__()
            self._attach_movie('chip', chip_movie)
            self._attach_movie('glow', glow_movie)

        def scopeWin(self, source):
            glow_movie = self.movies.get('glow')
            source.addEnable(glow_movie)
            source.addPlay(glow_movie)

    class Slot(object):
        def __init__(self, slot, socket, win_chip):
            self.slot = slot
            self.socket = socket
            self.chip = None
            self.win_chip = win_chip

        def attach(self, node):
            if node is None:
                return

            self.slot.addChild(node)

        def set_chip(self, chip):
            self.chip = chip

        def attach_chip(self, chip):
            self.attach(chip.get_node())
            self.set_chip(chip)

        def check_win(self):
            return self.chip is self.win_chip

        def scope_click(self, source):
            source.addTask("TaskNodeSocketClick", Socket=self.socket)

    class Path(object):
        def __init__(self, slot_from_id, slot_to_id, movie, tag):
            self.slot_from_id = slot_from_id
            self.slot_to_id = slot_to_id
            self.movie = movie
            self.node = self.movie.getMovieSlot('chip')
            self.tag = tag

        def get_node(self):
            return self.movie.getEntityNode()

        def attach_chip(self, chip):
            if chip is None:
                return

            self.node.addChild(chip.get_node())

        def scopePlay(self, source):
            self.movie.setLastFrame(False)
            source.addPlay(self.movie)

        def clean(self):
            if self.movie is not None:
                self.movie.onDestroy()
            self.movie = None
            self.node = None

    class PathFinder(object):
        def __init__(self):
            self.paths = []

        def add_path(self, path):
            self.paths.append(path)

        def get_path_from(self, slot_id, tag=None):
            for path in self.paths:
                if tag is not None and tag != path.tag:
                    continue
                if path.slot_from_id != slot_id:
                    continue
                return path
            return None

        def get_paths_to(self, slot_from_id, slot_to_id, tag=None):
            paths = []
            cur_slot_id = slot_from_id
            while cur_slot_id != slot_to_id:
                for path in self.paths:
                    if tag is not None and tag != path.tag:
                        continue
                    if path.slot_from_id != cur_slot_id:
                        continue
                    paths.append(path)
                    cur_slot_id = path.slot_to_id
                    break
                else:
                    return None
            return paths

        def clean(self):
            for path in self.paths:
                path.clean()

    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super(ChipMoveAtom, self).__init__()
        self.param = None
        self.tc = None

        self.slots = {}
        self.chips = {}
        self.path_finder = None

    def _onPreparation(self):
        super(ChipMoveAtom, self)._onPreparation()

    def _createMovie(self, name, type_movie, group_name, movie_name):
        if type_movie == "Movie2":
            return self._createMovie2(name, group_name, movie_name)
        else:
            return self._createMovie1(name, group_name, movie_name)

    def _createMovie1(self, name, group_name, movie_name):
        movie = ObjectManager.createObjectUnique('Movie', name, None, ResourceMovie="Movie{}_{}".format(group_name, movie_name))
        return movie

    def _createMovie2(self, name, group_name, movie_name):
        movie = ObjectManager.createObjectUnique('Movie2', name, None,
                                                 ResourceMovie="Movie2_{}".format(group_name), CompositionName=movie_name)
        return movie

    def _load_params(self):
        self.param = ChipMoveAtomManager.getParam(self.EnigmaName)

    def _setup(self):
        movie_slots_name = self.param.getMovieSlots()
        movie_slots = self.object.getObject(movie_slots_name)

        type_movie = self.param.TypeMovie
        group_name = self.object.getGroupName()

        for chip_id, chip_desc in self.param.getChips().iteritems():
            # create chip movies
            chip_movie = self._createMovie("Chip_{}".format(chip_id), type_movie, group_name, chip_desc.chip_movie_name)
            glow_movie = self._createMovie("Glow_{}".format(chip_id), type_movie, group_name, chip_desc.glow_movie_name)

            glow_movie.setEnable(False)

            new_chip = ChipMoveAtom.Chip(chip_movie, glow_movie)

            self.chips[chip_id] = new_chip

        for slot_id, slot_desc in self.param.getSlots().iteritems():
            slot_node = movie_slots.getMovieSlot(slot_desc.slot_name)
            socket_node = movie_slots.getSocket(slot_desc.socket_name)

            win_chip = self.chips.get(slot_desc.win_chip_id)
            new_slot = ChipMoveAtom.Slot(slot_node, socket_node, win_chip)
            slot_chip = self.chips.get(slot_desc.start_chip_id)

            new_slot.attach(slot_chip.get_node())
            new_slot.set_chip(slot_chip)

            self.slots[slot_id] = new_slot

        self.path_finder = ChipMoveAtom.PathFinder()
        for (slot_from_id, slot_to_id), path_desc in self.param.getPaths().iteritems():
            path_movie = self._createMovie("Path_{}_{}".format(slot_from_id, slot_to_id), type_movie, group_name, path_desc.movie_path)
            path = ChipMoveAtom.Path(slot_from_id, slot_to_id, path_movie, path_desc.tag)

            path_slot = self.slots.get(slot_from_id)
            path_slot.attach(path.get_node())

            self.path_finder.add_path(path)

    def _run_task_chains(self):
        ClickHolder = Holder()
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            for slot_id, race in tc.addRaceTaskList(self.slots):
                slot = self.slots.get(slot_id)
                race.addScope(slot.scope_click)
                race.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChipMoveAtom_SlotClick")
                race.addFunction(ClickHolder.set, slot_id)

            tc.addScope(self._scopeResolveClick, ClickHolder)
            tc.addScope(self._scopeCheckWin)

    def _scopeResolveClick(self, source, click_holder):
        slot_id = click_holder.get()

        path_forward = self.path_finder.get_path_from(slot_id, "Forward")

        if path_forward is None:
            return

        backward_paths = self.path_finder.get_paths_to(path_forward.slot_to_id, slot_id, "Backward")

        all_paths = [path_forward] + backward_paths

        for path, parallel in source.addParallelTaskList(all_paths):
            parallel.addScope(self._scopePath, path)

    def _scopePath(self, source, path):
        slot_from = self.slots.get(path.slot_from_id)
        slot_to = self.slots.get(path.slot_to_id)

        chip = slot_from.chip

        path.attach_chip(chip)

        source.addFunction(slot_from.set_chip, None)
        with source.addParallelTask(2) as (source_play, source_sound):
            source_play.addScope(path.scopePlay)
            source_sound.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChipMoveAtom_ChipMove")
        source.addFunction(slot_to.attach_chip, chip)

    def _scopeCheckWin(self, source):
        for slot in self.slots.itervalues():
            if slot.check_win() is False:
                return
        with source.addParallelTask(2) as (source_chips, source_sound):
            source_sound.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChipMoveAtom_Complete")
            for chip, parallel in source_chips.addParallelTaskList(self.chips.itervalues()):
                parallel.addScope(chip.scopeWin)
        source.addFunction(self.enigmaComplete)

    def _playEnigma(self):
        self._load_params()
        self._setup()
        self._run_task_chains()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._clean()
        self._playEnigma()

    def _clean(self):
        self.param = None

        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.slots = {}

        for chip in self.chips.itervalues():
            chip.clean()
        self.chips = {}

        self.path_finder.clean()
        self.path_finder = None

    def _onDeactivate(self):
        super(ChipMoveAtom, self)._onDeactivate()
        self._clean()
