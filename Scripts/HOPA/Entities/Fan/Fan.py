from Foundation.ArrowManager import ArrowManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.FanItemManager import FanItemManager
from HOPA.FanManager import FanManager

Enigma = Mengine.importEntity("Enigma")

class Fan(Enigma):
    STATE_MOVIEOPEN = 1
    STATE_OPEN = 2
    STATE_MOVIECLOSE = 3
    STATE_CLOSE = 4

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction("Polygon", Update=Fan._restorePolygon)
        Type.addActionActivate("Open", Update=Fan._updateOpen)

        Type.addActionActivate("FoundItems", Update=Fan._appendFoundItems)
        Type.addAction("FindItems")
        Type.addAction("Hint")
        Type.addAction("HoldOpen")
        pass

    def __init__(self):
        super(Fan, self).__init__()

        self.Movie_Open = None
        self.hotspot = None
        self.onSocketClickObserver = None
        self.item_linked_socket = {}
        self.socets = []
        self.state = Fan.STATE_CLOSE
        self.isComplete = None
        self.generedObjects = []
        self.slotItems = []
        self.forceClose = False
        self.lastFrame = False
        pass

    def _appendFoundItems(self, id, item):
        self.__cleanUp()
        self._disable_sockets()
        self._AttendMovieSlots("Movie_Open")
        pass

    def _onInitialize(self, obj):
        super(Fan, self)._onInitialize(obj)

        self.hotspot = Mengine.createNode("HotSpotPolygon")
        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        self.hotspot.disable()

        self.addChild(self.hotspot)
        pass

    def _onActivate(self):
        super(Fan, self)._onActivate()
        self.onSocketClickObserver = Notification.addObserver(Notificator.onSocketClick, self._onSocketClickFilter)

        if self.Open is False:
            return
            pass
        pass

    def _onDeactivate(self):
        super(Fan, self)._onDeactivate()
        Notification.removeObserver(self.onSocketClickObserver)
        if self.state is not Fan.STATE_CLOSE:
            self.object.setParam("HoldOpen", True)
            self.__cleanUp()
            self.object.setParam("Open", True)
            pass

        if self.hotspot:
            self.hotspot.setEventListener(None)
            self.hotspot.removeFromParent()
            Mengine.destroyNode(self.hotspot)
            self.hotspot = None
            pass
        pass

    def _updateOpen(self, value):
        if value is True:
            if self.state == Fan.STATE_OPEN or self.state == Fan.STATE_MOVIEOPEN or self.HoldOpen:
                self.openFan()
                return
                pass

            if self.state == Fan.STATE_MOVIECLOSE:
                TaskManager.cancelTaskChain("CloseFan")
                pass

            self.openFan()
            pass
        else:
            if self.state == Fan.STATE_CLOSE or self.state == Fan.STATE_MOVIECLOSE:
                return
                pass

            if self.state == Fan.STATE_MOVIEOPEN:
                TaskManager.cancelTaskChain("OpenFan")
                pass
            pass
        pass

    def _updateInteractive(self, value):
        if value is True:
            self.hotspot.enable()
            pass
        else:
            self.hotspot.disable()
            pass
        pass

    def _onMouseButtonEvent(self, context, event):
        if event.button != 0 or event.isDown is False:
            return True

        if self.state == Fan.STATE_OPEN:
            if ArrowManager.emptyArrowAttach() is False:
                return True
            else:
                FanManager.closeFan(self.object)
                pass
            return True

        if self.state == Fan.STATE_MOVIEOPEN:
            TaskManager.cancelTaskChain("OpenFan")
            FanManager.closeFan(self.object)
            return True

        if self.state == Fan.STATE_MOVIECLOSE:
            if TaskManager.existTaskChain("CloseFan") is True:
                TaskManager.cancelTaskChain("CloseFan")
                Notification.notify(Notificator.onFanCloseDone, True)

            FanManager.openFan(self.object)
            return True

        if self.state == Fan.STATE_CLOSE:
            FanManager.openFan(self.object)
            return True

        return True

    def _onSocketClickFilter(self, socket):
        if ArrowManager.emptyArrowAttach() is True:
            return False

        attach = ArrowManager.getArrowAttach()
        if socket not in self.socets:
            return False

        if self.item_linked_socket[attach] != socket:
            return False

        self.__onFanClick()

        return False

    ###Enigma
    def _playEnigma(self):
        self.object.setInteractive(True)
        FindItems = self.object.getFindItems()
        self.toFindItems = [objName for objName in FindItems if objName not in self.FoundItems]

        tc_name = "FanFindItem_%s" % (self.object.getName())
        with TaskManager.createTaskChain(Name=tc_name, Group=self.object, Cb=self._onFanComplete) as tc:
            SceneName = SceneManager.getCurrentSceneName()
            itemCount = len(self.toFindItems)

            with tc.addParallelTask(itemCount) as tcho:
                Group = self.object.getGroup()

                for tchog, ItemName in zip(tcho, self.toFindItems):
                    tchog.addTask("AliasFanFindItem", Fan=self.object, SceneName=SceneName, Group=Group, ItemName=ItemName)

            tc.addNotify(Notificator.onFanComplete, self.object)

    def _stopEnigma(self):
        self.object.setInteractive(False)
        if TaskManager.existTaskChain("FanFindItem_%s" % (self.object.name)) is True:
            TaskManager.cancelTaskChain("FanFindItem_%s" % (self.object.name))
            pass
        pass

    def _AttendMovieSlots(self, MovieName):
        fan_group = GroupManager.getGroup("Fan")
        FindItems = self.object.getFindItems()
        FoundItems = self.object.getFoundItems()
        countFindItems = len(FindItems)

        self.Movie_Open = fan_group.getObject(MovieName)
        Movie_Open_Entity = self.Movie_Open.getEntity()

        ObjList = [FanItemManager.getItemObject(item) for item in FindItems]

        for i in range(countFindItems):
            # ItemSprite
            itemName = FindItems[i]
            item = FanItemManager.getItemFanItem(itemName)

            id = "%d" % (i)
            slot = Movie_Open_Entity.getMovieSlot(id)

            gen_sprite = fan_group.generateObject("Gen_Sprite%d" % (i), "Sprite_Circle")
            self.generedObjects.append(gen_sprite)
            gen_sprite_entity = gen_sprite.getEntity()
            slot.addChild(gen_sprite_entity)

            item = item.getObject("Sprite_Item")
            self.slotItems.append(item)
            item_entity = item.getEntity()
            slot.addChild(item_entity)

            if itemName in FoundItems:
                continue
                pass

            gen_mask = fan_group.generateObject("Gen_BlackMask%d" % (i), "Sprite_Black")
            self.generedObjects.append(gen_mask)

            gen_mask_entity = gen_mask.getEntity()
            slot.addChild(gen_mask_entity)

            gen_socked = fan_group.generateObject("Gen_Socket%d" % (i), "Socket_Circle")
            self.generedObjects.append(gen_socked)
            gen_socked_entity = gen_socked.getEntity()
            slot.addChild(gen_socked_entity)

            gen_socked.setInteractive(True)

            self.socets.append(gen_socked)
            self.item_linked_socket[ObjList[i]] = gen_socked
            pass

        pass

    def openFan(self):
        self.hotspot.disable()
        self.state = Fan.STATE_MOVIEOPEN
        fan_group = GroupManager.getGroup("Fan")
        Movie_Open = fan_group.getObject("Movie_Open")
        pos = self.hotspot.getWorldPolygonCenter()
        Movie_Open.setPosition(pos)

        with TaskManager.createTaskChain(Name="OpenFan", Cb=Functor(self.__setOpened, Fan.STATE_OPEN)) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="Fan", Value=True)
            tc.addFunction(self._AttendMovieSlots, "Movie_Open")
            tc.addTask("TaskMoviePlay", Movie=Movie_Open, Wait=False, LastFrame=None, Reverse=False)
            if self.HoldOpen:
                tc.addTask("TaskMovieLastFrame", Movie=Movie_Open, Value=True)
                tc.addTask("TaskMovieStop", Movie=Movie_Open)
                pass
            pass
            self.object.setParam("HoldOpen", False)

    def closeFan(self):
        if self.object.getParam("Open") == True:
            self.object.setParam("Open", False)
            pass

        self.state = Fan.STATE_MOVIECLOSE
        Movie_Close = GroupManager.getObject("Fan", "Movie_Open")

        Movie_Close_Entity = Movie_Close.getEntity()
        pos = self.hotspot.getWorldPolygonCenter()
        Movie_Close.setPosition(pos)

        with TaskManager.createTaskChain(Name="CloseFan", Cb=Functor(self.__setOpened, Fan.STATE_CLOSE)) as tc:
            tc.addTask("TaskMoviePlay", Movie=Movie_Close, Wait=False, LastFrame=None, Reverse=True)
            tc.addTask("TaskMovieEnd", Movie=Movie_Close)
            tc.addFunction(self.__cleanUp)

            tc.addNotify(Notificator.onFanCloseDone)
            pass

        self._disable_sockets()
        pass

    def __cleanUp(self):
        for object in self.generedObjects:
            object.onDestroy()
            pass

        self.generedObjects = []

        for item in self.slotItems:
            entity = item.getEntity()
            entity.removeFromParent()
            pass

        self.slotItems = []

        self.Movie_Open = None
        pass

    def __setOpened(self, isSkip, state):
        self.state = state
        if not self.isComplete:
            self.hotspot.enable()

        pass

    def _disable_sockets(self):
        for soctet in self.socets:
            soctet.setInteractive(False)
            pass

        self.socets = []
        pass

    def skipActions(self):
        if TaskManager.existTaskChain("OpenFan") is True:
            TaskManager.cancelTaskChain("OpenFan")
            pass

        if self.state == Fan.STATE_OPEN:
            FanManager.closeFan(self.object)
            pass

        if TaskManager.existTaskChain("CloseFan") is True:
            TaskManager.cancelTaskChain("CloseFan")
            pass

    def _onFanComplete(self, isSkip):
        self.hotspot.disable()
        self.object.setParam("Play", False)
        FanManager.closeFan(self.object)

        self.object.setParam("FoundItems", [])

        self.isComplete = True
        self.enigmaComplete()
        self.hotspot.setEventListener(None)
        self.hotspot.removeFromParent()
        Mengine.destroyNode(self.hotspot)
        self.hotspot = None
        pass

    def _restorePolygon(self, value):
        self.hotspot.setPolygon(value)
        pass

    def __onFanClick(self):
        Notification.notify(Notificator.onFanClick, self.object)
        pass
