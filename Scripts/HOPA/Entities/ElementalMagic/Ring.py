from Foundation.Initializer import Initializer
from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from Foundation.SceneManager import SceneManager
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

        self.__state = "Idle"
        self.SemaphoreReady = Semaphore(False, "RingReady")
        self.tc = None

        self._root = None
        self.Movies = {}
        self.magic = None

        self._easing_mode = ElementalMagicManager.getConfig("RingReturnTween", "easyLinear")
        self._easing_speed = ElementalMagicManager.getConfig("RingReturnSpeed", 1.0)

        self.EventUpdateState = Event("onRingStateUpdate")

    def _onInitialize(self, owner, current_element=None):
        self._owner = owner

        slot = owner.getRingSlot()
        # this node will be attached to cursor
        root = Mengine.createNode("Interender")
        root.setName("ElementalMagicRing")
        slot.addChild(root)
        self._root = root

        for state, (movie_name, play, loop) in ElementalMagicManager.getRingMovieParams().items():
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

        self.magic = MagicEffect()
        self.magic.onInitialize(slot=self._root)

        if current_element is not None:
            self.magic.setElement(current_element)

        if ElementalMagicManager.isMagicReady():
            self.__state = "Ready"
            self.SemaphoreReady.setValue(True)

    def onActivate(self):
        self._runTaskChain()

    def _onFinalize(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.magic.onFinalize()
        self.magic = None

        for movie in self.Movies.values():
            movie.returnToParent()
        self.Movies = {}

        if self.isAttachedToCursor() is True:
            self._detachFromCursor()

        Mengine.destroyNode(self._root)
        self._root = None

        self.__state = None

        self.SemaphoreReady = None
        self.EventUpdateState = None

    def _runTaskChain(self):
        Scopes = dict(
            Idle=Functor(self.__stateIdle, self.Movies.get("Idle")),
            Ready=Functor(self.__stateReady, self.Movies.get("Ready")),
            Attach=Functor(self.__stateAttach, self.Movies.get("Attach")),
            Return=Functor(self.__stateReturn, self.Movies.get("Return")),
            Pick=Functor(self.__statePick, self.Movies.get("Pick")),
            Use=Functor(self.__stateUse, self.Movies.get("Use")),
        )

        self.tc = TaskManager.createTaskChain(Name="ElementalMagicRing", Repeat=True, NoCheckAntiStackCycle=True)

        with self.tc as tc:
            def __states(isSkip, cb):
                Trace.msg_dev("    Ring: run state {}".format(self.__state))
                cb(isSkip, self.__state)

            tc.addScopeSwitch(Scopes, __states)

    def getState(self):
        return self.__state

    def __setState(self, state):
        prev_state = self.__state
        self.__state = state
        self.EventUpdateState(prev_state, state)

    def __stateIdle(self, source, Movie):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addEnable(Movie)
            parallel_1.addFunction(self.magic.setState, "Idle")
            parallel_1.addScope(self.magic.scopePlayCurrentState, Wait=False, Loop=True)

        with source.addRaceTask(4) as (source_attach, source_mouse, source_ready, source_pick):
            source_attach.addScope(self.__scopeTryStateAttach, Movie)

            source_mouse.addScope(self.__scopeMouseOverHandler, Movie)

            source_ready.addSemaphore(self.SemaphoreReady, From=True)
            source_ready.addFunction(self.__setState, "Ready")

            source_pick.addListener(Notificator.onElementalMagicPick)
            source_pick.addFunction(self.__setState, "Pick")

        source.addDisable(Movie)

    def __stateReady(self, source, Movie):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addEnable(Movie)
            parallel_1.addFunction(self.magic.setState, "Ready")
            parallel_1.addScope(self.magic.scopePlayCurrentState, Wait=False, Loop=True)

        with source.addRaceTask(3) as (source_attach, source_mouse, source_idle):
            source_attach.addScope(self.__scopeTryStateAttach, Movie)

            source_mouse.addScope(self.__scopeMouseOverHandler, Movie)

            source_idle.addSemaphore(self.SemaphoreReady, From=False)
            source_idle.addFunction(self.__setState, "Idle")

        source.addDisable(Movie)

    def __stateAttach(self, source, Movie):
        # attach root to arrow
        source.addFunction(self._root.removeFromParent)
        source.addNotify(Notificator.onElementalMagicRingMouseLeave, self)
        source.addFunction(self._attachToCursor)

        source.addEnable(self.getBaseStateMovie() or Movie)

        with source.addRaceTask(4) as (source_use, source_pick, source_invalid, source_miss):
            source_use.addListener(Notificator.onElementalMagicUse)     # from macro
            source_use.addFunction(self.__setState, "Use")

            source_pick.addListener(Notificator.onElementalMagicPick)     # from macro
            source_pick.addFunction(self.__setState, "Pick")

            source_invalid.addListener(Notificator.onElementalMagicInvalidClick)
            source_invalid.addFunction(self.__setState, "Return")

            source_miss.addScope(self.__scopeMissClickHandler)

        source.addDisable(self.getBaseStateMovie() or Movie)

    def __stateReturn(self, source, Movie):
        if self.isAttachedToCursor() is False:
            source.addFunction(self.__setState, "Idle")
            return

        source.addNotify(Notificator.onElementalMagicRingMouseLeave, self)

        if Movie is None:
            source.addEnable(self.getBaseStateMovie())

            source.addScope(self.__scopeReturnToParent)
            source.addFunction(self.__setState, "Idle")

            source.addDisable(self.getBaseStateMovie())
            return

        source.addEnable(Movie)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addScope(self.__scopeReturnToParent)

        source.addFunction(self.__setState, "Idle")

        source.addDisable(Movie)

    def __stateUse(self, source, Movie):
        if Movie is None:
            source.addEnable(self.getBaseStateMovie())

            source.addFunction(self.magic.setState, "Release")
            source.addScope(self.magic.scopePlayCurrentState, Wait=True)
            # source.addNotify(Notificator.onElementalMagicRelease, self.magic.getElement())
            source.addFunction(self.__setState, "Return")

            source.addDisable(self.getBaseStateMovie())
            return

        source.addEnable(Movie)

        # maybe I should detach from cursor and attach to temp node at mouse position
        with source.addParalellTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addFunction(self.magic.setState, "Release")
            parallel_1.addScope(self.magic.scopePlayCurrentState, Wait=True)
            parallel_1.addFunction(self.magic.removeElement)

        source.addFunction(self.__setState, "Return")

        source.addDisable(Movie)

    def __statePick(self, source, Movie):
        if Movie is None:
            source.addEnable(self.getBaseStateMovie())

            source.addFunction(self.magic.setState, "Appear")
            source.addScope(self.magic.scopePlayCurrentState, Wait=True)
            source.addFunction(self.__setState, "Return")

            source.addDisable(self.getBaseStateMovie())
            return

        source.addEnable(Movie)

        # maybe I should detach from cursor and attach to temp node at mouse position
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
            parallel_1.addFunction(self.magic.setState, "Appear")
            parallel_1.addScope(self.magic.scopePlayCurrentState, Wait=True)

        source.addFunction(self.__setState, "Return")

        source.addDisable(Movie)

    # scopes

    def __scopeMissClickHandler(self, source):
        with source.addRepeatTask() as (repeat, until):
            repeat.addTask("TaskMouseButtonClick", isDown=True)
            with repeat.addRaceTask(2) as (zoom, miss):
                zoom.addListener(Notificator.onZoomOpen)
                miss.addDelay(10)
                miss.addNotify(Notificator.onElementalMagicInvalidClick, InvalidClick.Miss)
                miss.addFunction(self.__setState, "Return")

            until.addBlock()    # onElementalMagicInvalidClick updates state

    def __scopeTryStateAttach(self, source, Movie):
        with source.addRepeatTask() as (repeat, until):
            repeat.addTask("TaskMovie2SocketClick", Movie2=Movie, SocketName="socket")
            with repeat.addIfTask(ArrowManager.emptyArrowAttach) as (repeat_true, repeat_false):
                repeat_true.addFunction(self.__setState, "Attach")

            until.addEvent(self.EventUpdateState, lambda _, new_state: new_state == "Attach")

    def __scopeMouseOverHandler(self, source, Movie):
        with source.addRepeatTask() as (repeat, until):
            repeat.addTask("TaskMovie2SocketEnter", SocketName="socket", Movie2=Movie)
            repeat.addNotify(Notificator.onElementalMagicRingMouseEnter, self)
            repeat.addTask("TaskMovie2SocketLeave", SocketName="socket", Movie2=Movie)
            repeat.addNotify(Notificator.onElementalMagicRingMouseLeave, self)

            until.addBlock()

    def __scopeReturnToParent(self, source):
        arrow_node = Mengine.getArrowNode()
        Point1 = arrow_node.getWorldPosition()
        ring_slot = self._owner.getRingSlot()
        Point2 = ring_slot.getWorldPosition()

        effect_layer_name = "InventoryItemEffect"
        scene = SceneManager.getCurrentScene()
        if scene.hasSlot(effect_layer_name):
            layer = scene.getSlot(effect_layer_name)
        else:
            if _DEVELOPMENT is True:
                Trace.log("Entity", 2, "ElementalMagic Ring: Not found slot {!r} to make bezier return effect".format(effect_layer_name))
            layer = self._owner

        if layer is None:
            source.addFunction(self._detachFromCursor)
            source.addFunction(self._returnRingToParent)
            return

        node = Mengine.createNode("Interender")
        node.setLocalPosition(Point1)

        layer.addChild(node)

        self._detachFromCursor()
        node.addChild(self._root)

        source.addTask("TaskNodeBezier2To", Node=node, Point1=Point1, To=Point2,
                       Speed=self._easing_speed, Easing=self._easing_mode)
        source.addFunction(self._returnRingToParent, True)
        source.addTask("TaskNodeDestroy", Node=node)

    # utils

    def setReady(self, state):
        self.SemaphoreReady.setValue(state)

    def getBaseStateMovie(self):
        if self.SemaphoreReady.getValue() is True:
            return self.Movies["Ready"]
        else:
            return self.Movies["Idle"]

    def getRootNode(self):
        return self._root

    def _returnRingToParent(self, with_remove=False):
        """ add root to the Ring slot (please check if root is detached from arrow) """
        if with_remove is True:
            self._root.removeFromParent()
        slot = self._owner.getRingSlot()
        slot.addChild(self._root)

    def _attachToCursor(self):
        arrow_node = Mengine.getArrowNode()
        ArrowManager.attachArrow(self._root)
        arrow_node.addChildFront(self._root)

    def _detachFromCursor(self):
        arrow_attach = ArrowManager.getArrowAttach()
        if _DEVELOPMENT is True:
            assert self.isAttachedToCursor(), "You tried detach root from arrow, but arrow_attach {} != root {}".format(arrow_attach, self._root)
        arrow_attach.removeFromParent()
        ArrowManager.removeArrowAttach()

    def isAttachedToCursor(self):
        arrow_attach = ArrowManager.getArrowAttach()
        return arrow_attach == self._root
