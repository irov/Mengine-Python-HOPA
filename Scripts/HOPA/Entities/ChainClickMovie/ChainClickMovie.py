from Foundation import Utils
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.ChainClickMovieManager import ChainClickMovieManager
from Holder import Holder


Enigma = Mengine.importEntity("Enigma")


class Slot(object):
    def __init__(self, SlotID, Socket, Node):
        self.id = SlotID
        self.socket = Socket
        self.node = Node

        self.chip = None

    def getID(self):
        return self.id

    def clickScope(self, source):
        if self.socket is None:
            return

        source.addTask('TaskNodeSocketClick', Socket=self.socket)

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
        self.chip.attachToNode(self.node)

    def destroy(self):
        chip = self.getChip()
        chip.destroy()

        self.id = None
        self.socket = None
        self.node = None
        self.chip = None


class Chip(object):
    def __init__(self, MovieIdle, MovieSelected, MovieFail, MakeMovieFunc):
        self.state = None

        self.movies = dict(Idle=MakeMovieFunc(MovieIdle, Enable=False, Play=True, Loop=True),
                           Selected=MakeMovieFunc(MovieSelected, Enable=False, Play=True, Loop=False),
                           Fail=MakeMovieFunc(MovieFail, Enable=False, Play=True, Loop=False))

        self.node = Mengine.createNode('Interender')

        for movie in self.movies.itervalues():
            if movie is None:
                continue

            movie_entity_node = movie.getEntityNode()
            self.node.addChild(movie_entity_node)

    def getNode(self):
        return self.node

    def attachToNode(self, Node):
        if Node is None:
            return

        self.detachFromParent()

        Node.addChild(self.node)

    def playMovieState(self, source, NewState):
        self.changeState(NewState)

        if self.state != NewState:
            return

        Movie = self.getMovie()

        source.addPlay(Movie)

    def getMovie(self):
        return self.movies.get(self.state)

    def changeState(self, NewState):
        if NewState is None:
            return

        CurStateMovie = self.movies.get(self.state)
        if CurStateMovie is not None:
            CurStateMovie.setEnable(False)

        NewStateMovie = self.movies.get(NewState)
        if NewStateMovie is None:
            return

        NewStateMovie.setEnable(True)

        self.state = NewState

    def detachFromParent(self):
        if self.node.hasParent() is True:
            self.node.removeFromParent()

    def destroy(self):
        self.detachFromParent()

        for movie in self.movies.itervalues():
            movie.onDestroy()

        self.movies = {}

        Mengine.destroyNode(self.node)
        self.node = None

        self.state = None


class ChainClickMovie(Enigma):
    def __init__(self):
        super(ChainClickMovie, self).__init__()

        self.param = None
        self.slots = []

        self.tc = None

        self.MovieSlots = None

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def __loadParams(self):
        self.param = ChainClickMovieManager.getParam(self.EnigmaName)

    def __setup(self):
        if self.param is None:
            msg = "Enigma {}: self.param is None on setup stage".format(self.EnigmaName)
            Trace.log("Entity", 0, msg)
            return

        MovieSlotsName = self.param.getMovieSlotsName()
        if MovieSlotsName is None:
            msg = "Enigma {}: MovieSlotsName in Param is None".format(self.EnigmaName)
            Trace.log("Entity", 0, msg)
            return

        self.MovieSlots = self.object.getObject(MovieSlotsName)
        if self.MovieSlots is None:
            return

        slots_data = self.param.getSlots()

        MovieSlotsEntityNode = self.MovieSlots.getEntityNode()

        slots = []
        for slot_id, slot_param in slots_data.iteritems():
            Socket = self.MovieSlots.getSocket(slot_param.Socket)
            slot = Slot(slot_id, Socket, MovieSlotsEntityNode)

            slots.append(slot)

            chip = Chip(slot_param.MovieChipIdle, slot_param.MovieChipSelected, slot_param.MovieChipFail, self._makeMovie)
            slot.setChip(chip)

            slot.chip.changeState('Idle')
        self.slots = slots

    def _makeMovie(self, MovieName, **Params):
        if MovieName is None:
            return None

        GroupName = self.object.getGroupName()
        if GroupName is None:
            return None

        Movie = Utils.makeMovie2(GroupName, MovieName, **Params)

        return Movie

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for slot in self.slots:
            slot.destroy()

        self.slots = []

        self.MovieSlots = None

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def __runTaskChain(self):
        ClickHolder = Holder()
        ClickChainHolder = Holder([])

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addFunction(self.__updateSlots, ClickChainHolder)

            for slot, tc_race in tc.addRaceTaskList(self.slots):
                tc_race.addScope(slot.clickScope)
                tc_race.addFunction(ClickHolder.set, slot)

            tc.addScope(self.__resolveClickScope, ClickHolder, ClickChainHolder)

    def __resolveClickScope(self, source, ClickHolder, ClickChainHolder):
        ClickSlot = ClickHolder.get()
        ClickChain = ClickChainHolder.get()

        if ClickSlot is None:
            return

        ClickSlotID = ClickSlot.getID()

        if not self.param.Repit:
            if ClickSlotID in ClickChain:
                return

        ClickChain.append(ClickSlotID)

        if self.__checkChain(ClickChain):
            source.addFunction(ClickSlot.chip.changeState, 'Selected')
            source.addFunction(self.__checkComplete, ClickChain)
        else:
            source.addNotify(Notificator.onSoundEffectOnObject, self.object, "ChainClickMovie_FailClick")
            source.addScope(ClickSlot.chip.playMovieState, 'Fail')
            source.addFunction(ClickChainHolder.set, [])

    def __updateSlots(self, ClickChainHolder):
        ClickChain = ClickChainHolder.get()
        for slot in self.slots:
            if slot.getID() in ClickChain:
                continue

            slot.chip.changeState('Idle')

    def __checkChain(self, chain):
        param_chain = self.param.getChain()
        for click_id, valid_id in zip(chain, param_chain):
            if isinstance(valid_id, list) and click_id in valid_id:
                continue
            if click_id != valid_id:
                return False
        return True

    def __checkComplete(self, chain):
        param_chain = self.param.getChain()

        if len(param_chain) != len(chain):
            return
        for cur_id, valid_id in zip(chain, param_chain):
            if isinstance(valid_id, list) and cur_id in valid_id:
                continue
            if cur_id != valid_id:
                return

        self.enigmaComplete()

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ChainClickMovie, self)._onPreparation()
        self.__loadParams()
        self.__setup()

    def _onDeactivate(self):
        super(ChainClickMovie, self)._onDeactivate()
        self.__cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.__runTaskChain()

    def _restoreEnigma(self):
        self.__runTaskChain()

    def _stopEnigma(self):
        if self.tc is not None:
            self.tc.cancel()

    def _resetEnigma(self):
        self.__cleanUp()
        self.__setup()
        self.__runTaskChain()
