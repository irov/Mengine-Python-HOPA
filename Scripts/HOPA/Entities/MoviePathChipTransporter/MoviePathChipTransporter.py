from Foundation.Notificator import Notificator
from Foundation.ObjectManager import ObjectManager
from Foundation.TaskManager import TaskManager
from HOPA.MoviePathChipTransporterManager import MoviePathChipTransporterManager
from Holder import Holder

Enigma = Mengine.importEntity("Enigma")

class MoviePathChipTransporter(Enigma):
    # - service classes ----------------------------------------------
    class Slot(object):
        def __init__(self, slot, socket):
            self.slot = slot
            self.socket = socket

            self.movies = {}

        def getPosition(self):
            return self.slot.getLocalPosition()

        def addMovie(self, name, movie):
            self.attachMovie(movie)
            self.movies[name] = movie

        def attachMovie(self, movie):
            movie_entity_node = movie.getEntityNode()
            self.slot.addChild(movie_entity_node)

        def setChip(self, chip):
            chip.attach(self.slot)

        def clickScope(self, source):
            source.addTask('TaskNodeSocketClick', Socket=self.socket)

    class Chip(object):
        def __init__(self, movie):
            self.movie = movie

        def attach(self, node):
            movie_entity_node = self.movie.getEntityNode()
            node.addChild(movie_entity_node)

        def detach(self):
            movie_entity_node = self.movie.getEntityNode()
            movie_entity_node.removeFromParent()

    class PathFinder(object):
        def __init__(self, paths, graph):
            self.paths = paths if paths is not None else {}
            self.graph = graph if graph is not None else {}

        def hasPathFromTo(self, from_slot_id, to_slot_id):
            return (from_slot_id, to_slot_id) in self.graph

        def getPathMovieFromTo(self, from_slot_id, to_slot_id):
            path_id = self.graph.get((from_slot_id, to_slot_id))
            return self.paths.get(path_id)

    # ---------------------------------------------------------------

    def __init__(self):
        super(MoviePathChipTransporter, self).__init__()

        self.tc = None
        self.param = None

        self.chip = None
        self.slots = {}
        self.path_finder = None

        self.current_slot_id = None
        self.win_slot_id_chain = None

        self.movies = []
        self.effect_node = None

    def load_data(self):
        self.param = MoviePathChipTransporterManager.getParam(self.EnigmaName)

    def setup(self):
        MovieSlotsName = self.param.MovieSlots
        MovieChipName = self.param.MovieChip

        MovieSlots = self.generateMovieOnNode(MovieSlotsName, self.node)

        MovieChip = self.generateMovieOnNode(MovieChipName)
        self.chip = MoviePathChipTransporter.Chip(MovieChip)
        self.win_slot_id_chain = self.param.WinSlotsChain

        self.effect_node = Mengine.createNode('Interender')
        self.node.addChild(self.effect_node)

        for SlotID, (SlotName, SocketName, MovieSelected) in self.param.SlotsDict.iteritems():
            slot = MovieSlots.getMovieSlot(SlotName)
            socket = MovieSlots.getSocket(SocketName)

            SlotObject = MoviePathChipTransporter.Slot(slot, socket)

            if MovieSelected is not None:
                movie_selected = self.generateMovieOnNode(MovieSelected, Enable=False)
                SlotObject.addMovie('Selected', movie_selected)

            if SlotID == self.param.StartSlot:
                SlotObject.setChip(self.chip)
                self.current_slot_id = SlotID

                movie_selected = SlotObject.movies.get('Selected')
                if movie_selected is not None:
                    movie_selected.setEnable(True)

            self.slots[SlotID] = SlotObject

        paths, graph = self.param.PathsDict, self.param.GraphDict

        path_movies = {}

        for path_id, movie_path_name in paths.iteritems():
            movie_path = self.generateMovieOnNode(movie_path_name, self.effect_node)
            path_movies[path_id] = movie_path

        self.path_finder = MoviePathChipTransporter.PathFinder(path_movies, graph)

    def generateMovieOnNode(self, MovieName, AttachNode=None, Enable=True):
        GroupName = self.object.getGroupName()
        MoviePosition = [0.0, 0.0]
        movie = ObjectManager.createObjectUnique('Movie2', MovieName, None, ResourceMovie="Movie2_" + GroupName, CompositionName=MovieName, Position=MoviePosition, Enable=Enable, Interactive=True)

        if AttachNode is not None:
            AttachNode.addChild(movie.getEntityNode())
        self.movies.append(movie)

        return movie

    def _onPreparation(self):
        super(MoviePathChipTransporter, self)._onPreparation()
        self.load_data()
        self.setup()

    def resolveClickScope(self, source, click_slot_id_holder, click_chain_holder):
        slot_id = click_slot_id_holder.get()
        slot_id_chain = click_chain_holder.get()

        source.addNotify(Notificator.onEnigmaSlotClick)

        if slot_id in slot_id_chain:
            return

        if self.path_finder.hasPathFromTo(self.current_slot_id, slot_id) is False:
            return

        slot_id_chain.append(slot_id)

        source.addScope(self.chipMoveToScope, slot_id)

    def chipMoveToScope(self, source, slot_id):
        path = self.path_finder.getPathMovieFromTo(self.current_slot_id, slot_id)

        if path is None:
            return

        current_slot = self.slots.get(self.current_slot_id)
        current_slot.slot.addChild(path.getEntityNode())

        source.addNotify(Notificator.onEnigmaChipMove)
        source.addScope(self.playPathScope, path)

        self.current_slot_id = slot_id

    def playPathScope(self, source, movie_path):
        slot = self.slots.get(self.current_slot_id)
        movie_slot = movie_path.getMovieSlot('chip')

        source.addTask('TaskMovie2Rewind', Movie2=movie_path)
        source.addFunction(self.chip.attach, movie_slot)
        source.addTask("TaskMovie2Play", Movie2=movie_path)
        source.addFunction(slot.setChip, self.chip)

    def updateSlotsScope(self, source, click_chain_holder):
        chain = click_chain_holder.get()
        source.addScope(self._updateSlotsScope, chain)

    def _updateSlotsScope(self, source, chain):
        for slot_id, slot in self.slots.iteritems():
            if 'Selected' not in slot.movies:
                continue
            movie = slot.movies.get('Selected')
            if slot_id in chain:
                source.addEnable(movie)
            else:
                source.addDisable(movie)

    def checkCompleteScope(self, source, click_chain_holder):
        slot_chain = click_chain_holder.get()

        if slot_chain == self.win_slot_id_chain:
            source.addFunction(self.enigmaComplete)
            return

        part_win_chain = self.win_slot_id_chain[:len(slot_chain)]
        if slot_chain != part_win_chain:
            source.addScope(self.chipMoveToStartScope, slot_chain)

    def chipMoveToStartScope(self, source, slot_chain):
        count = len(slot_chain) - 1
        with source.addForTask(count) as (it, tc_for):
            def _scope(scope_source, slot_chain):
                slot_chain.pop()
                to_slot_id = slot_chain[-1]
                scope_source.addScope(self._updateSlotsScope, slot_chain)
                scope_source.addScope(self.chipMoveToScope, to_slot_id)

            tc_for.addScope(_scope, slot_chain)

    def _playEnigma(self):
        ClickSlotHolder = Holder()
        ClickChainHolder = Holder([self.current_slot_id, ])

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            for (slot_id, slot), race in tc.addRaceTaskList(self.slots.iteritems()):
                race.addScope(slot.clickScope)
                race.addFunction(ClickSlotHolder.set, slot_id)

            tc.addScope(self.resolveClickScope, ClickSlotHolder, ClickChainHolder)
            tc.addScope(self.updateSlotsScope, ClickChainHolder)
            tc.addScope(self.checkCompleteScope, ClickChainHolder)

    def _pauseEnigma(self):
        self._stopEnigma()

    def _skipEnigmaScope(self, source):
        slot_index = self.win_slot_id_chain.index(self.current_slot_id) + 1
        slot_chain = list(self.win_slot_id_chain[slot_index:])

        count = len(slot_chain)

        with source.addForTask(count) as (it, tc_for):
            def _scope(scope_source, slot_chain):
                to_slot_id = slot_chain.pop(0)

                slot_index = self.win_slot_id_chain.index(to_slot_id)
                update_chain = self.win_slot_id_chain[:slot_index]

                scope_source.addScope(self._updateSlotsScope, update_chain)
                scope_source.addScope(self.chipMoveToScope, to_slot_id)

            tc_for.addScope(_scope, slot_chain)

    def _clean_resources(self):
        self.param = None

        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        for movie in reversed(self.movies):
            movie.getEntityNode().removeFromParent()
            movie.onDeactivate()
            movie.onFinalize()
            movie.onDestroy()

        if self.effect_node is not None:
            self.effect_node.removeFromParent()
            Mengine.destroyNode(self.effect_node)
            self.effect_node = None

        self.movies = []

        self.chip = None
        self.slots = {}
        self.path_finder = None

        self.current_slot_id = None
        self.win_slot_id_chain = None

    def _onFinalize(self):
        super(MoviePathChipTransporter, self)._onFinalize()
        self._clean_resources()

    def _restoreEnigma(self):
        self._playEnigma()