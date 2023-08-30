from Foundation.Initializer import Initializer
from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.Entities.ElementalMagic.MagicEffect import MagicEffect


class InvalidClick(object):
    Miss = 0
    WrongElement = 1
    WrongPlace = 2


class Ring(Initializer):

    def __init__(self):
        super(Ring, self).__init__()
        self._owner = None
        self.state = "Idle"
        self._root = None
        self.Movies = {}
        self.magic = MagicEffect()
        self.tc = None

    def _onInitialize(self, owner, current_element=None):
        self._owner = owner

        slot = owner.getRingSlot()
        # this node will be attached to cursor
        root = Mengine.createNode("Interender")
        slot.addChild(root)
        self._root = root

        for state, movie_name in ElementalMagicManager.getRingUIStates().items():
            movie = self._owner.object.getObject(movie_name)
            movie.setEnable(False)
            movie.setPlay(True)
            movie.setLoop(True)
            movie.setInteractive(True)

            node = movie.getEntityNode()
            node.removeFromParent()
            root.addChild(node)

            self.Movies[state] = movie

        self.magic.onInitialize()

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
                cb(isSkip, self.state)

            tc.addScopeSwitch(Scopes, __states)

    def __setState(self, state):
        self.state = state

    def __stateIdle(self, source, Movie):
        source.addFunction(self.magic.setState, "Idle")
        source.addEnable(Movie)

        with source.addRaceTask(2) as (source_attach, source_ready):
            source_attach.addTask("TaskMovie2Click", Movie2=Movie)
            source_attach.addFunction(self.__setState, "Attach")

            source_ready.addListener(Notificator.onElementalMagicReady)
            source_ready.addFunction(self.__setState, "Ready")

        source.addDisable(Movie)

    def __stateReady(self, source, Movie):
        source.addFunction(self.magic.setState, "Ready")
        source.addEnable(Movie)

        source.addTask("TaskMovie2Click", Movie2=Movie)
        source.addFunction(self.__setState, "Attach")

        source.addDisable(Movie)
        pass

    def __stateAttach(self, source, Movie):
        MovieReady = self.Movies["Ready"]

        # attach root to arrow
        source.addFunction(self._root.removeFromParent)
        source.addFunction(self._attachToCursor, self._root)

        if Movie is not None:
            source.addEnable(Movie)
        else:
            source.addEnable(MovieReady)

        with source.addRaceTask(3) as (source_use, source_pick, source_invalid):
            source_use.addListener(Notificator.onElementalMagicUse)     # from macro
            source_use.addFunction(self.__setState, "Use")

            source_pick.addListener(Notificator.onElementalMagicPick)     # from macro
            source_pick.addFunction(self.__setState, "Pick")

            source_invalid.addTask("TaskMouseButtonClick", isDown=False)
            source_invalid.addNotify(Notificator.onElementalMagicInvalidClick, InvalidClick.Miss)
            source_invalid.addFunction(self.__setState, "Return")

        if Movie is not None:
            source.addDisable(Movie)
        else:
            source.addDisable(MovieReady)

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
        """
        # todo: fly to toolbar - ref PolicyEffectInventoryAddInventoryItemWithItemPopup
        node = Mengine.createNode("Interender")
        self._detachFromCursor(self._root)
        node.addChild(self._root)

        Point1 = ArrowManager.getArrow().getWorldPosition()
        ring_slot = self._owner.getRingSlot()
        Point2 = ring_slot.getWorldPosition()

        source.addTask("TaskNodeBezier2To", Node=node, Point1=Point1, To=Point2, Speed=0.5)
        source.addTask("TaskNodeDestroy", Node=node)
        """
        source.addFunction(self._returnRingToParent)

    def _returnRingToParent(self):
        self._root.removeFromParent()
        slot = self._owner.getRingSlot()
        slot.addChild(self._root)

    def _attachToCursor(self, node):
        arrow = ArrowManager.getArrow()
        ArrowManager.attachArrow(node)
        arrow.addChildFront(node)

    def _detachFromCursor(self, node):
        arrow_attach = ArrowManager.getArrowAttach()
        if arrow_attach != node:
            node.removeFromParent()     # fixme: remove from parent, but it wasn't on arrow
            return
        arrow_attach.removeFromParent()
        ArrowManager.removeArrowAttach()

