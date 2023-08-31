from Foundation.Initializer import Initializer
from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.Entities.ElementalMagic.MagicEffect import MagicEffect


class InvalidClick(object):
    Miss = 0
    WrongElement = 1
    EmptyRing = 2


class Ring(Initializer):

    def __init__(self):
        super(Ring, self).__init__()
        self._owner = None

        self.state = "Idle"
        self._prev_state = None
        self.tc = None

        self._root = None
        self.Movies = {}
        self.magic = MagicEffect()

        self.EventUpdateState = Event("onStateUpdate")

    def _onInitialize(self, owner, current_element=None):
        self._owner = owner

        slot = owner.getRingSlot()
        # this node will be attached to cursor
        root = Mengine.createNode("Interender")
        root.setName("ElementalMagicRing")
        slot.addChild(root)
        self._root = root

        for state, [movie_name, play, loop] in ElementalMagicManager.getRingMovieParams().items():
            if movie_name is None:
                continue

            if self._owner.object.hasObject(movie_name) is False:
                Trace.log("Entity", 0, "Ring._onInitialize: not found movie %s for state %s" % (movie_name, state))
                continue

            movie = self._owner.object.getObject(movie_name)
            movie.setEnable(False)
            movie.setPlay(play)
            movie.setLoop(loop)
            movie.setInteractive(True)

            node = movie.getEntityNode()
            node.removeFromParent()
            root.addChild(node)

            self.Movies[state] = movie

        self.magic.onInitialize(slot=self._root)

        if current_element is not None:
            self.magic.setElement(current_element)

        if ElementalMagicManager.isMagicReady():
            self.state = "Ready"

    def onActivate(self):
        self._runTaskChain()

    def onFinalize(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.magic.onFinalize()
        self.magic = None

        for movie in self.Movies.values():
            movie.returnToParent()
        self.Movies = {}

        Mengine.destroyNode(self._root)
        self._root = None

    def _runTaskChain(self):
        Scopes = dict(
            Idle=Functor(self.__stateIdle, self.Movies.get("Idle")),
            Ready=Functor(self.__stateReady, self.Movies.get("Ready")),
            Attach=Functor(self.__stateAttach, self.Movies.get("Attach")),
            Return=Functor(self.__stateReturn, self.Movies.get("Return")),
            Pick=Functor(self.__statePick, self.Movies.get("Pick")),
            Use=Functor(self.__stateUse, self.Movies.get("Use")),
        )

        self.tc = TaskManager.createTaskChain(Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as tc:
            def __states(isSkip, cb):
                print "    Ring: run state", self.state
                cb(isSkip, self.state)

            tc.addScopeSwitch(Scopes, __states)

    def __setState(self, state):
        print "    Ring: set state", self.state, "->", state
        self._prev_state = self.state
        self.state = state
        self.EventUpdateState(self._prev_state, self.state)

    def __scopeTryStateAttach(self, source, Movie):
        with source.addRepeatTask() as (repeat, until):
            repeat.addTask("TaskMovie2SocketClick", Movie2=Movie, SocketName="socket")
            with repeat.addIfTask(ArrowManager.emptyArrowAttach) as (repeat_true, repeat_false):
                repeat_true.addFunction(self.__setState, "Attach")

            until.addEvent(self.EventUpdateState, lambda _, new_state: new_state == "Attach")

    def __stateIdle(self, source, Movie):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addEnable(Movie)
            parallel_1.addFunction(self.magic.setState, "Idle")

        with source.addRaceTask(3) as (source_attach, source_ready, source_pick):
            source_attach.addScope(self.__scopeTryStateAttach, Movie)

            source_ready.addListener(Notificator.onElementalMagicReady)
            source_ready.addFunction(self.__setState, "Ready")

            source_pick.addListener(Notificator.onElementalMagicPick)
            source_pick.addFunction(self.__setState, "Pick")

        source.addDisable(Movie)

    def __stateReady(self, source, Movie):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addFunction(self.magic.setState, "Ready")
            parallel_1.addEnable(Movie)

        with source.addRaceTask(2) as (source_attach, source_idle):
            source_attach.addScope(self.__scopeTryStateAttach, Movie)

            source_idle.addListener(Notificator.onElementalMagicReadyEnd)       # todo
            source_idle.addFunction(self.__setState, "Idle")

        source.addDisable(Movie)

    def __stateAttach(self, source, Movie):
        # attach root to arrow
        source.addFunction(self._root.removeFromParent)
        source.addFunction(self._attachToCursor)

        if Movie is not None:
            source.addEnable(Movie)
        else:
            source.addEnable(self.Movies[self._prev_state])

        with source.addRaceTask(4) as (source_use, source_pick, source_invalid, source_miss):
            source_use.addListener(Notificator.onElementalMagicUse)     # from macro
            source_use.addFunction(self.__setState, "Use")

            source_pick.addListener(Notificator.onElementalMagicPick)     # from macro
            source_pick.addFunction(self.__setState, "Pick")

            source_invalid.addListener(Notificator.onElementalMagicInvalidClick)
            source_invalid.addFunction(self.__setState, "Return")

            source_miss.addTask("TaskMouseButtonClick", isDown=False)
            source_miss.addNotify(Notificator.onElementalMagicInvalidClick, InvalidClick.Miss)
            source_miss.addFunction(self.__setState, "Return")

        if Movie is not None:
            source.addDisable(Movie)
        else:
            source.addDisable(self.Movies[self._prev_state])

    def __stateReturn(self, source, Movie):
        if Movie is None:
            source.addScope(self.__scopeReturnToParent)
            source.addFunction(self.__setState, "Idle")
            return

        source.addEnable(Movie)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addScope(self.__scopeReturnToParent)

        source.addFunction(self.__setState, "Idle")

        source.addDisable(Movie)
        pass

    def __stateUse(self, source, Movie):
        if Movie is None:
            source.addFunction(self.__setState, "Return")
            return

        source.addEnable(Movie)

        # maybe I should detach from cursor and attach to temp node at mouse position
        with source.addParalellTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addFunction(self.magic.setState, "Release")
            parallel_1.addTask("TaskMovie2Play", Movie2=self.magic.getCurrentMovie(), Wait=True)
            parallel_1.addFunction(self.magic.removeElement)

        source.addFunction(self.__setState, "Return")

        source.addDisable(Movie)
        pass

    def __statePick(self, source, Movie):
        if Movie is None:
            source.addFunction(self.magic.setState, "Appear")
            source.addTask("TaskMovie2Play", Movie2=self.magic.getCurrentMovie(), Wait=True)
            source.addFunction(self.__setState, "Return")
            return

        source.addEnable(Movie)

        # maybe I should detach from cursor and attach to temp node at mouse position
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addFunction(self.magic.setState, "Appear")
            parallel_1.addTask("TaskMovie2Play", Movie2=self.magic.getCurrentMovie(), Wait=True)

        source.addFunction(self.__setState, "Return")

        source.addDisable(Movie)
        pass

    # utils

    def __scopeReturnToParent(self, source):
        source.addFunction(self._detachFromCursor)
        """
        # todo: fly to toolbar - ref PolicyEffectInventoryAddInventoryItemWithItemPopup
        node = Mengine.createNode("Interender")
        node.addChild(self._root)

        Point1 = ArrowManager.getArrow().getWorldPosition()
        ring_slot = self._owner.getRingSlot()
        Point2 = ring_slot.getWorldPosition()

        source.addTask("TaskNodeBezier2To", Node=node, Point1=Point1, To=Point2, Speed=0.5)
        source.addTask("TaskNodeDestroy", Node=node)
        """
        source.addFunction(self._returnRingToParent)

    def _returnRingToParent(self):
        """ add root to the Ring slot (please check if root is detached from arrow) """
        if _DEVELOPMENT is True:
            assert ArrowManager.getArrowAttach() != self._root, "Can't return root, because it attached to arrow"
        slot = self._owner.getRingSlot()
        slot.addChild(self._root)

    def _attachToCursor(self):
        arrow = ArrowManager.getArrow()
        ArrowManager.attachArrow(self._root)
        arrow.addChildFront(self._root)

    def _detachFromCursor(self):
        arrow_attach = ArrowManager.getArrowAttach()
        if _DEVELOPMENT is True:
            assert arrow_attach == self._root, "You tried detach root from arrow, but arrow_attach {} != root {}".format(arrow_attach, self._root)
        arrow_attach.removeFromParent()
        ArrowManager.removeArrowAttach()

