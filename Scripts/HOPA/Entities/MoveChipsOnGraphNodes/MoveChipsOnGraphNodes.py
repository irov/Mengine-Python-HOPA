from Foundation import Utils
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.MoveChipsOnGraphNodesManager import MoveChipsOnGraphNodesManager


Enigma = Mengine.importEntity("Enigma")


class Graph(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self.complete = False

    def __setComplete(self):
        for node in self.nodes.values():
            if not node.win_chip_placed:
                return
        self.complete = True

    def __findPath(self, node_from):
        path = self.nodes[node_from.id].edges_to
        for node_id in path:
            node = self.nodes[node_id]
            if node.chip is None:
                return node

    def getNodeWithChipByID(self, chip_id):
        for node in self.nodes.values():
            if node.chip is None:
                continue
            if node.chip.id is chip_id:
                return node

    def isComplete(self):
        return self.complete

    def scopeMoveChip(self, source, node_from, cb_add_child, time=400.0):
        if node_from.chip is None:
            return

        node_to = self.__findPath(node_from)
        if node_to is None:
            source.addFunction(node_from.changeChipState, 'idle')
            return

        chip = node_from.chip
        chip_node = chip.node

        pos_from = chip_node.getWorldPosition()
        pos_to = node_to.slot.getWorldPosition()

        cb_add_child(chip_node)

        move_fx = chip.movies.get('move_fx')
        if move_fx is not None:
            en_move_fx = move_fx.getEntityNode()
            cb_add_child(en_move_fx)
            en_move_fx.setWorldPosition(pos_from)
            move_fx.setEnable(True)

            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskMovie2Play", Movie2=move_fx)
                tc.addDisable(move_fx)

        source.addTask("TaskNodeMoveTo", Node=chip_node, From=pos_from, To=pos_to, Time=time)
        source.addFunction(chip_node.setLocalPosition, (0.0, 0.0))
        source.addFunction(node_from.detachChip)
        source.addFunction(node_to.attachChip, chip)

        with source.addIfTask(node_to.winChipIsPlaced) as (source_true, source_false):
            source_true.addFunction(node_to.changeChipState, 'placed')
            source_false.addFunction(node_to.changeChipState, 'idle')
        source.addFunction(self.__setComplete)


class Node(object):
    def __init__(self, id_, socket, slot, win_chip_id, edges_to, saved_slots_chip):
        self.id = id_
        self.socket = socket
        self.slot = slot
        self.win_chip_id = win_chip_id
        self.edges_to = edges_to

        self.chip = None
        self.win_chip_placed = False

        if self.win_chip_id is None:
            self.win_chip_placed = True

        self.saved_slots_chip = saved_slots_chip

    def __setWinChipPlaced(self):
        if self.win_chip_id is None:
            return

        if self.chip.id is self.win_chip_id:
            self.win_chip_placed = True
        else:
            self.win_chip_placed = False

    def changeChipState(self, state):
        if self.chip is not None:
            self.chip.changeState(state)

    def winChipIsPlaced(self):
        return self.win_chip_placed and self.win_chip_id is not None

    def scopeMouseClick(self, source):
        source.addTask("TaskNodeSocketClick", isDown=True, Socket=self.socket)

    def scopeMouseEnter(self, source):
        source.addTask("TaskNodeSocketEnter", Socket=self.socket)

    def scopeMouseLeave(self, source):
        source.addTask("TaskNodeSocketLeave", Socket=self.socket)

    def attachChip(self, chip):
        self.chip = chip
        self.saved_slots_chip[self.id] = chip.id
        self.chip.attachToMovieSlot(self.slot)
        self.__setWinChipPlaced()

    def detachChip(self):
        if self.chip is not None:
            self.chip.detachFromParent()
            self.saved_slots_chip[self.id] = None
            self.chip = None

    def destroy(self):
        if self.chip is not None:
            self.chip.destroy()


class Chip(object):
    def __init__(self, id_, cb_make_movie):
        self.id = id_
        self.state = None

        self.movies = dict(idle=cb_make_movie(id_ + '_idle', Enable=False),
                           selected=cb_make_movie(id_ + '_selected', Enable=False),
                           placed=cb_make_movie(id_ + '_placed', Enable=False),
                           move_fx=cb_make_movie('move_fx', Enable=False, Name='move_fx_' + id_))

        self.node = Mengine.createNode('Interender')

        for movie in self.movies.values():
            if movie is None:
                continue

            movie_entity_node = movie.getEntityNode()
            self.node.addChild(movie_entity_node)

    def changeState(self, new_state):
        if new_state is None:
            return

        cur_state_movie = self.movies.get(self.state)
        if cur_state_movie is not None:
            cur_state_movie.setEnable(False)

        new_state_movie = self.movies.get(new_state)
        if new_state_movie is None:
            return

        new_state_movie.setLastFrame(False)
        new_state_movie.setEnable(True)
        new_state_movie.setPlay(True)
        self.state = new_state

    def attachToMovieSlot(self, movie_slot):
        self.detachFromParent()
        movie_slot.addChild(self.node)

    def detachFromParent(self):
        if self.node.hasParent() is True:
            self.node.removeFromParent()

    def destroy(self):
        self.detachFromParent()

        for movie in self.movies.values():
            movie_entity_node = movie.getEntityNode()
            movie_entity_node.removeFromParent()
            movie.onFinalize()
            movie.onDestroy()

        Mengine.destroyNode(self.node)
        self.node = None


class MoveChipsOnGraphNodes(Enigma):
    def __init__(self):
        super(MoveChipsOnGraphNodes, self).__init__()
        self.tc = None
        self.semaphore = None

        self.param = None
        self.graph = None

    @staticmethod
    def declareORM(type_):
        Enigma.declareORM(type_)
        type_.addAction(type_, 'savedSlotChips')

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def loadParam(self):
        self.param = MoveChipsOnGraphNodesManager.getParam(self.EnigmaName)

    def makeMovie(self, movie_name, **Params):
        if movie_name is None:
            return
        group_name = self.object.getGroupName()
        return Utils.makeMovie2(group_name, movie_name, **Params)

    def setup(self, restore=False):
        nodes = dict()

        movies_slots = self.object.getObject('Movie2_Slots')
        nodes_params = self.param.nodes
        for node_name, node_params in nodes_params.items():
            chip_name = node_params[0] if restore is False else self.savedSlotChips[node_name]
            win_chip_name = node_params[1]
            edges_to_name_list = node_params[2]

            socket = movies_slots.getSocket('socket_' + node_name)
            slot = movies_slots.getMovieSlot('slot_' + node_name)
            node = Node(node_name, socket, slot, win_chip_name, edges_to_name_list, self.savedSlotChips)
            if chip_name is not None:
                chip = Chip(chip_name, self.makeMovie)
                node.attachChip(chip)

                if node.winChipIsPlaced() is True:
                    node.changeChipState('placed')
                else:
                    node.changeChipState('idle')

            nodes[node_name] = node

        self.graph = Graph(nodes)

    def cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()

        if self.graph is not None:
            for node in self.graph.nodes.values():
                node.destroy()

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def scopeMove(self, source):
        for node, race_source in source.addRaceTaskList(self.graph.nodes.values()):
            race_source.addScope(node.scopeMouseEnter)
            race_source.addFunction(node.changeChipState, 'selected')

            with race_source.addRaceTask(2) as (leave_source, click_source):
                leave_source.addScope(node.scopeMouseLeave)
                leave_source.addSemaphore(self.semaphore, From=True, To=False)
                with leave_source.addIfTask(node.winChipIsPlaced) as (source_true, source_false):
                    source_true.addFunction(node.changeChipState, 'placed')
                    source_false.addFunction(node.changeChipState, 'idle')

                click_source.addScope(node.scopeMouseClick)
                click_source.addSemaphore(self.semaphore, From=True, To=False)
                click_source.addScope(self.graph.scopeMoveChip, node, self.addChild, time=self.param.move_time)

    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        self.semaphore = Semaphore(True, 'MoveChipsOnGraphNodes')
        with self.tc as tc:
            tc.addSemaphore(self.semaphore, To=True)
            tc.addScope(self.scopeMove)

            with tc.addIfTask(self.graph.isComplete) as (complete_source, _):
                complete_source.addFunction(self.enigmaComplete)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(MoveChipsOnGraphNodes, self)._onPreparation()
        self.loadParam()
        self.setup()

        # # /// enable save/load  # if self.Playing is False:  #     self.setup()  # else:  #     self.setup(restore=True)

    def _onActivate(self):
        super(MoveChipsOnGraphNodes, self)._onActivate()

    def _onDeactivate(self):
        super(MoveChipsOnGraphNodes, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):  # on first run
        self.runTaskChain()

    def _stopEnigma(self):  # when exit and complete
        if self.tc is not None:
            self.tc.cancel()

    def _restoreEnigma(self):  # when not first run
        self.runTaskChain()

    def _pauseEnigma(self):  # when exit and not complete
        return

    def _resetEnigma(self):  # when reset button activated
        self.cleanUp()
        self.setup()
        self.runTaskChain()

    def _skipEnigmaScope(self, source):  # when skip button activated
        self.tc.cancel()

        for node_to, parallel in source.addParallelTaskList(self.graph.nodes.values()):
            if node_to.win_chip_id is None or node_to.winChipIsPlaced():
                continue
            node_from = self.graph.getNodeWithChipByID(node_to.win_chip_id)
            if node_from is None:
                continue

            self.addChild(node_from.chip.node)
            parallel.addFunction(node_from.changeChipState, 'selected')
            parallel.addTask("TaskNodeMoveTo", Node=node_from.chip.node, From=node_from.slot.getWorldPosition(),
                             To=node_to.slot.getWorldPosition(), Time=self.param.move_time * 2)
            parallel.addFunction(node_from.changeChipState, 'placed')
