from Event import Event
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.System.SystemCruiseControl import CRUISE_LOG, CruiseControlCursorSpeed
from HOPA.ZoomManager import ZoomManager


class AliasCruiseControlAction(TaskAlias):
    pos_zero = Mengine.vec3f(0.0, 0.0, 0.0)
    __clickEmulatedEvent = Event("AliasCruiseControlClickEmulated")  # this is will trigger checkClickSuccess logic
    __semaphoreClickSuccess = Semaphore(False, "AliasCruiseControlClickSuccess")

    fakeHotSpotClickEventParams = (0, -1, -1, 0, 1, 1, 1)  # touchId, x, y, button, pressure, isDown, isPressed

    def __init__(self):
        super(AliasCruiseControlAction, self).__init__()

    def _onParams(self, params):
        super(AliasCruiseControlAction, self)._onParams(params)
        self.Position = params.get("Position", None)
        self.Object = params.get("Object", None)
        self.ObjectParams = params.get("ObjectParams", [None, False])

        self.Speed = params.get("Speed", CruiseControlCursorSpeed)

    def _onInitialize(self):
        super(AliasCruiseControlAction, self)._onInitialize()
        self.Node = Mengine.getArrowNode()

    def _onValidate(self):
        super(AliasCruiseControlAction, self)._onValidate()
        if self.Object is None and self.Position is None:
            self.validateFailed("AliasCruiseControlAction should have Object or Position param")

    def __getClickPosition(self):
        obj_type = self.Object.getType() if self.Object else None
        getPosFn = AliasCruiseControlAction.getObjectPos.get(obj_type, AliasCruiseControlAction.getPosZero)

        pos = getPosFn(self)
        if pos is None:
            pos = self.getPosZero(self)

        return pos

    def __setClickPosition(self):
        if self.Position is None:
            self.Position = self.__getClickPosition()

    def __setClickSuccessObserver(self, source):
        obj_type = self.Object.getType() if self.Object else None
        scopeCheckClickSuccess = AliasCruiseControlAction.checkClickSuccessObservers.get(
            obj_type, AliasCruiseControlAction.checkClickSuccessNone)

        with source.addFork() as (fork_source):
            fork_source.addEvent(self.__clickEmulatedEvent)

            with fork_source.addRaceTask(2) as (source_success, source_fail):
                scopeCheckClickSuccess(source_success, self)  # unpack scopes to upper level
                source_success.addSemaphore(self.__semaphoreClickSuccess, To=True)

                source_fail.addDelay(0.0)
                source_fail.addDelay(0.0)
                source_fail.addDelay(0.0)

                # if three frames elapsed, there almost guarantee, click is not successful
                # we triggering fake click and expecting that scopeCheckClickSuccess will be executed
                source_fail.addScope(self.__handleClickFake)
                source_fail.addBlock()  # make sure that this fork will ends only through source_success

    def __handleClickFake(self, source):
        obj_type = self.Object.getType() if self.Object else None
        handleClickFakeScope = AliasCruiseControlAction.handleClickFakeScopes.get(
            obj_type, AliasCruiseControlAction.handleClickFakeNone)

        source.addFunction(self.__fakeClickLog)
        source.addScope(handleClickFakeScope, self)

    def __fakeClickLog(self):
        if not self.Object:
            return

        objName = self.Object.getName()

        groupName = None
        group = self.Object.getGroup()
        if group is not None:
            groupName = group.getName()

        parentName = None
        if self.Object.isActive():
            node = self.Object.getEntityNode()
            parentNode = node.getParent()
            if parentNode is not None:
                parentName = parentNode.getName()

        msg = "[AliasCruiseControlAction] FAKE_CLICK_TRIGGERED can't click: {}, group: {}, parent: {}. Maybe change it's hotspot or hintPoint".format(objName, groupName, parentName)
        CRUISE_LOG(msg)

    def __scopeEmulateClick(self, source):
        source.addTask("TaskNodeMoveTo", Node=self.Node, To=self.Position, Speed=self.Speed, Easing="easyCubicOut")
        source.addTask("TaskCursorSetPosition", Position=self.Position)
        source.addDelay(0)
        source.addTask("TaskCursorClickEmulate", Position=self.Position, Value=True)
        source.addFunction(self.__clickEmulatedEvent)
        source.addDelay(0)
        source.addDelay(0)
        source.addTask("TaskCursorClickEmulate", Position=self.Position, Value=False)

    def _onGenerate(self, source):
        self.__waitObjectEnable(source)  # crazy stuff here, this is for SystemUnittest object click detection

        # after simulated click happened, check if it successful, then set __semaphoreClickSuccess to True if so
        self.__setClickSuccessObserver(source)

        source.addFunction(self.__setClickPosition)

        # make emulated click, calls __clickEmulatedEvent
        source.addScope(self.__scopeEmulateClick)

        # if click successful -> end AliasTask, if not try to click until it be successful
        # by default SystemCruiseControl gives 5 sec to complete alias, if not it will be skipped
        source.addSemaphore(self.__semaphoreClickSuccess, From=True, To=False)

    """ Object click position detection START """

    @staticmethod
    def getPosMovieButtonObj(self):
        return self.Object.getCurrentMovieSocketCenter()

    @staticmethod
    def getPosMovieObj(self):
        if self.Object.isActive():
            socket = None

            socket_name = self.ObjectParams[0] if len(self.ObjectParams) > 0 else None
            if socket_name is not None and socket_name != -1:
                socket = self.Object.getSocket(socket_name)

            if socket is None:
                sockets = self.Object.entity.movie.getSockets()
                if len(sockets) > 0:
                    socket = sockets[0][2]  # if socket wasn't specified, get first

            if socket is None:  # if no sockets in movie, then return zero pos
                pos = self.pos_zero
            else:
                pos = socket.getWorldPolygonCenter()

            return pos

    @staticmethod
    def getPosInteractionObj(self):
        return self.Object.calcWorldHintPoint()

    @staticmethod
    def getPosMovieItemObj(self):
        movie_item_entity = self.Object.getEntity()

        if movie_item_entity is not None:
            return movie_item_entity.getHintPoint()

    @staticmethod
    def getPosSpriteObj(self):
        # fixme probably not working right

        sprite_entity = self.Object.getEntity()

        if sprite_entity is not None:
            return sprite_entity.sprite.getWorldImageCenter()

    @staticmethod
    def getPosZero(self):
        return self.pos_zero

    """ Object click position detection END"""

    """ """

    """ Object clicked observers START """

    def __listenerFilterObjIsEqual(self, obj, *args):
        return obj == self.Object

    def __listenerFilterOnZoomEnter(self, zoomGroupName, *args):
        return ZoomManager.hasZoomGroupName(zoomGroupName)

    def __listenerFilterObjIsEqualDbg(self, obj):
        msg = "checkClickSuccess: listenerFilterObjIsEqualDbg {} {} {}".format(obj == self.Object, obj.getName(), self.Object.getName())
        CRUISE_LOG(msg)
        print(msg)
        return obj == self.Object

    @staticmethod
    def checkClickSuccessMovieButtonObj(source, self):
        source.addListener(Notificator.onMovieButtonClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessMovie2ButtonObj(source, self):
        source.addListener(Notificator.onMovie2ButtonClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessMovieItemObj(source, self):
        source.addListener(Notificator.onMovieItemClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessMovie2Obj(source, self):
        onSocketButtonEvent = self.Object.onMovieSocketButtonEvent
        source.addEvent(onSocketButtonEvent, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessInteractionObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onInteractionClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onInteractionClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessSocketObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onSocketClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onSocketClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessButtonObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onButtonClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onButtonClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessTransitionObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onTransitionClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onTransitionClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessItemObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onItemClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onItemClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessZoomObj(source, self):
        with source.addRaceTask(2) as (race_0, race_1):
            race_0.addListener(Notificator.onZoomClickBegin, Filter=self.__listenerFilterObjIsEqual)
            race_1.addListener(Notificator.onZoomClick, Filter=self.__listenerFilterObjIsEqual)

    @staticmethod
    def checkClickSuccessNone(source, self):
        source.addDelay(0.0)

    """ Object clicked observers END """

    """ Object handle fake click START """

    @staticmethod
    def handleClickFakeNone(source, self):
        # source.addSemaphore(self.__semaphoreClickSuccess, To=True)
        source.addDelay(0.0)

    @staticmethod
    def handleClickFakeMovie2Obj(source, self):
        if self.Object.isActive():
            movieEntity = self.Object.getEntity()
            socket = movieEntity.getSocket("socket")
            eventation = socket.getEventation()

            source.addFunction(eventation.callEvent, "onHandleMouseButtonEvent", self.fakeHotSpotClickEventParams)

    @staticmethod
    def handleClickFakeZoomObj(source, self):
        # zoomEntry = ZoomManager.getZoomEntryByObject(self.Object)
        # if zoomEntry:
        #     source.addFunction(ZoomManager.openZoom, zoomEntry.zoomGroupName)

        source.addNotify(Notificator.onZoomClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addFunction(ZoomManager.openZoom, {})".format(zoomEntry.zoomGroupName)
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeMovie2ButtonObj(source, self):
        source.addNotify(Notificator.onMovie2ButtonClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onMovie2ButtonClick, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeMovieButtonObj(source, self):
        source.addNotify(Notificator.onMovieButtonClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onMovieButtonClick, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeMovieItemObj(source, self):
        source.addNotify(Notificator.onMovieItemClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onMovieItemClick, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeItemObj(source, self):
        # source.addNotify(Notificator.onItemClickBegin, self.Object)
        source.addNotify(Notificator.onItemClick, self.Object, 0.0, 0.0)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onItemClickBegin, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeSocketObj(source, self):
        # source.addNotify(Notificator.onSocketClickBegin, self.Object)
        source.addNotify(Notificator.onSocketClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onSocketClickBegin, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeInteractionObj(source, self):
        # source.addNotify(Notificator.onInteractionClickBegin, self.Object)
        source.addNotify(Notificator.onInteractionClick, self.Object)

        # def lambdaMsg():
        #     msg = " source.addNotify(Notificator.onInteractionClickBegin, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeTransitionObj(source, self):
        # source.addNotify(Notificator.onTransitionClickBegin, self.Object)
        source.addNotify(Notificator.onTransitionClick, self.Object)

        # def lambdaMsg():
        #     msg = "source.addNotify(Notificator.onTransitionClickBegin, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    @staticmethod
    def handleClickFakeButtonObj(source, self):
        # source.addNotify(Notificator.onButtonClickBegin, self.Object)
        source.addNotify(Notificator.onButtonClick, self.Object)

        # def lambdaMsg():
        #     msg = " source.addNotify(Notificator.onButtonClickBegin, {})".format(self.Object.getName())
        #     print msg
        #     CRUISE_LOG(msg)
        #
        # source.addFunction(lambdaMsg)

    """ Object handle fake click END """

    """ for SystemUnittest """

    @staticmethod
    def __cb_obj_parent_visitor_check_enable(parent):
        if not parent.getEnable():
            return False

    def __checkEnableObjectRecursive(self):
        all_parent_objects_enabled = self.Object.visitParentBrakeOnFalse(self.__cb_obj_parent_visitor_check_enable)
        object_enabled = self.Object.getEnable()
        return all([all_parent_objects_enabled, object_enabled])

    # DEPRECATED
    def __waitObjectEnable(self, source):
        if self.Object is not None and self.ObjectParams[1] and not self.__checkEnableObjectRecursive():
            # print '::: TaskActionClick Wait Until Obj {} will be enabled...'.format(self.Object.getName())
            semaphore_obj_enabled = Semaphore(False, 'AliasCruiseControlObjEnabled')

            def scopeEventObjEnable(source_):
                with source_.addFork() as fork_source:
                    with fork_source.addRepeatTask() as (repeat_source, until_source):
                        with repeat_source.addIfTask(self.__checkEnableObjectRecursive) as (true_source, _):
                            true_source.addSemaphore(semaphore_obj_enabled, To=True)

                        repeat_source.addDelay(10)
                        until_source.addSemaphore(semaphore_obj_enabled, From=True)

            source.addScope(scopeEventObjEnable)
            source.addSemaphore(semaphore_obj_enabled, From=True)
            source.addDelay(2000)

    """ """


""" Pos detection functions mapping to object type 
    This is used when Alias received Object and not Click Position
"""
AliasCruiseControlAction.getObjectPos = {
    'ObjectMovie2Button': AliasCruiseControlAction.getPosMovieButtonObj,
    'ObjectMovieButton': AliasCruiseControlAction.getPosMovieButtonObj,
    'ObjectMovie2CheckBox': AliasCruiseControlAction.getPosMovieButtonObj,
    'ObjectMovieCheckBox': AliasCruiseControlAction.getPosMovieButtonObj,
    'ObjectMovie2': AliasCruiseControlAction.getPosMovieObj,
    'ObjectMovie': AliasCruiseControlAction.getPosMovieObj,
    'ObjectZoom': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectSocket': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectInteraction': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectTransition': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectButton': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectItem': AliasCruiseControlAction.getPosInteractionObj,
    'ObjectMovieItem': AliasCruiseControlAction.getPosMovieItemObj,
    'ObjectMovie2Item': AliasCruiseControlAction.getPosMovieItemObj,
    'ObjectSprite': AliasCruiseControlAction.getPosSpriteObj,
    'ObjectInventoryItem': AliasCruiseControlAction.getPosSpriteObj,
    'ObjectInventoryCountItem': AliasCruiseControlAction.getPosSpriteObj,
    'ObjectFan': AliasCruiseControlAction.getPosZero,
}

""" Clicked object observer mapping to object type """
AliasCruiseControlAction.checkClickSuccessObservers = {
    'ObjectMovie2Button': AliasCruiseControlAction.checkClickSuccessMovie2ButtonObj,
    'ObjectMovieButton': AliasCruiseControlAction.checkClickSuccessMovieButtonObj,
    'ObjectMovie2CheckBox': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectMovieCheckBox': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectMovie2': AliasCruiseControlAction.checkClickSuccessMovie2Obj,
    'ObjectMovie': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectZoom': AliasCruiseControlAction.checkClickSuccessZoomObj,
    'ObjectSocket': AliasCruiseControlAction.checkClickSuccessSocketObj,
    'ObjectInteraction': AliasCruiseControlAction.checkClickSuccessInteractionObj,
    'ObjectTransition': AliasCruiseControlAction.checkClickSuccessTransitionObj,
    'ObjectButton': AliasCruiseControlAction.checkClickSuccessButtonObj,
    'ObjectItem': AliasCruiseControlAction.checkClickSuccessItemObj,
    'ObjectMovieItem': AliasCruiseControlAction.checkClickSuccessMovieItemObj,
    'ObjectMovie2Item': AliasCruiseControlAction.checkClickSuccessMovieItemObj,
    'ObjectSprite': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectInventoryItem': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectInventoryCountItem': AliasCruiseControlAction.checkClickSuccessNone,
    'ObjectFan': AliasCruiseControlAction.checkClickSuccessNone,
}

""" Handle click fake scopes mapping """

AliasCruiseControlAction.handleClickFakeScopes = {
    'ObjectMovie2Button': AliasCruiseControlAction.handleClickFakeMovie2ButtonObj,
    'ObjectMovieButton': AliasCruiseControlAction.handleClickFakeMovieButtonObj,
    'ObjectMovie2CheckBox': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectMovieCheckBox': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectMovie2': AliasCruiseControlAction.handleClickFakeMovie2Obj,
    'ObjectMovie': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectZoom': AliasCruiseControlAction.handleClickFakeZoomObj,
    'ObjectSocket': AliasCruiseControlAction.handleClickFakeSocketObj,
    'ObjectInteraction': AliasCruiseControlAction.handleClickFakeInteractionObj,
    'ObjectTransition': AliasCruiseControlAction.handleClickFakeTransitionObj,
    'ObjectButton': AliasCruiseControlAction.handleClickFakeButtonObj,
    'ObjectItem': AliasCruiseControlAction.handleClickFakeItemObj,
    'ObjectMovieItem': AliasCruiseControlAction.handleClickFakeMovieItemObj,
    'ObjectMovie2Item': AliasCruiseControlAction.handleClickFakeMovieItemObj,
    'ObjectSprite': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectInventoryItem': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectInventoryCountItem': AliasCruiseControlAction.handleClickFakeNone,
    'ObjectFan': AliasCruiseControlAction.handleClickFakeNone,
}
