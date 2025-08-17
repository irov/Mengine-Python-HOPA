from Foundation.System import System
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager
from HOPA.QuestManager import QuestManager
from HOPA.ScenarioManager import ScenarioManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class SystemItemPlusScene(System):
    Open_Zoom = None

    def __init__(self):
        super(SystemItemPlusScene, self).__init__()
        self.items_Inventort = {}
        self.items_Inventort_Keys = {}
        self.items_Scenes_Glob = {}
        self.tc_Fade = None
        self.tc_Fade_close = None
        self.Node_Fade = Mengine.createNode("Interender")
        self.Node_Fade.setName("ItemPlus_Fade_Node")
        self.posTo = [0.0, 0.0]
        self.posFrom = [0.0, 0.0]

        # Defaults
        self.ItemPlusInventoryName = DefaultManager.getDefault("ItemPlusInventoryName", "Inventory")
        self.ItemPlusDefaultName = DefaultManager.getDefault("ItemPlusDefaultName", "ItemPlusDefault")
        self.ItemPlusFadeGroup = DefaultManager.getDefault("ItemPlusFadeGroup", "FadeZoom")
        self.ItemPlusFadeValue = DefaultManager.getDefaultFloat("ItemPlusFadeValue", 0.60)

        self.ItemPlusOpenFadeTime = DefaultManager.getDefaultFloat("ItemPlusOpenFadeTime", 700.0)
        self.ItemPlusOpenMoveTime = DefaultManager.getDefaultFloat("ItemPlusOpenMoveTime", 700.0)
        self.ItemPlusOpenScaleTime = DefaultManager.getDefaultFloat("ItemPlusOpenScaleTime", 700.0)
        self.ItemPlusOpenAlphaTime = DefaultManager.getDefaultFloat("ItemPlusOpenAlphaTime", 700.0 * 0.33)

        self.ItemPlusCloseFadeTime = DefaultManager.getDefaultFloat("ItemPlusCloseFadeTime", 700.0)
        self.ItemPlusCloseMoveTime = DefaultManager.getDefaultFloat("ItemPlusCloseMoveTime", 700.0)
        self.ItemPlusCloseScaleTime = DefaultManager.getDefaultFloat("ItemPlusCloseScaleTime", 700.0)
        self.ItemPlusCloseAlphaTime = DefaultManager.getDefaultFloat("ItemPlusCloseAlphaTime", 700.0 * 0.33)
        self.ItemPlusCloseAlphaDelay = DefaultManager.getDefaultFloat("ItemPlusCloseAlphaDelay", 700.0 * 0.66)

    def _onRun(self):
        self.addObserver(Notificator.onGetItem, self._itemGet)
        self.addObserver(Notificator.onInventoryActivate, self.__onInventoryActivate)
        self.addObserver(Notificator.onInventoryAppendInventoryItem, self._itemAppentInvItem)

        self.addObserver(Notificator.onInventoryRemoveItem, self._itemRemove)

        self.addObserver(Notificator.onItemZoomEnter, self._OpenZoom)
        self.addObserver(Notificator.onItemZoomLeaveOpenZoom, self._CloseZoom)

        self.addObserver(Notificator.onSceneActivate, self._AddChildren)
        self.addObserver(Notificator.onSceneDeactivate, self._RemChildren)
        self.addObserver(Notificator.onScenarioComplete, self._close_Self)

        return True

    def _ItemPlus_Activate(self):
        for key in self.items_Inventort:
            itemInManager = ItemManager.getItem(key)
            ScenePlus = itemInManager.PlusScene
            groupName = SceneManager.getSceneMainGroupName(ScenePlus)
            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(ScenePlus, groupName)

            Movies = self.items_Inventort[key][1]

            if hasSceneActiveQuest and Movies[2] == 'Idle':
                Movies[0].setEnable(False)
                Movies[1].setEnable(True)
                Movies[2] = 'Ready'
            elif not hasSceneActiveQuest and Movies[2] == 'Ready':
                Movies[0].setEnable(True)
                Movies[1].setEnable(False)
                Movies[2] = 'Idle'

            self.items_Inventort[key][1] = Movies
        return False

    def __onInventoryActivate(self, inventory):
        self.InitExtra()
        self._ItemPlus_Activate()

        return False

    def _close_Self(self, ScenarioID):
        if self.hasOpenItemPlus() is False:
            return False

        if ScenarioID.endswith("_Tutorial") is True:
            return False

        scenGr = ScenarioManager.getScenarioGroupName(ScenarioID)
        if scenGr in self.items_Scenes_Glob:
            Notification.notify(Notificator.onItemZoomLeaveOpenZoom)
        return False

    @staticmethod
    def hasOpenItemPlus():
        return SystemItemPlusScene.Open_Zoom is not None

    @staticmethod
    def getOpenItemPlusName():
        scene_name = None
        if SystemItemPlusScene.hasOpenItemPlus():
            scene_name = SystemItemPlusScene.Open_Zoom[1]
        return scene_name

    def InitExtra(self):
        for key in self.items_Inventort_Keys:
            if (self.items_Inventort.has_key(key) is True):
                continue
            self._AddItem(key)

    def _itemAppentInvItem(self, item):
        self._itemGet(None, item)
        return False

    def _itemGet(self, inventory, item):
        self._ItemPlus_Activate()
        for key, val in self.items_Inventort.iteritems():
            if (val[0] == item):
                return False

        itemName = ItemManager.getInventoryItemKey(item)

        addItem = self._AddItem(itemName)

        if addItem is True:
            self.items_Inventort_Keys[itemName] = [itemName]

            itemInManager = ItemManager.getItem(itemName)
            ScenePlus = itemInManager.PlusScene
            self.items_Scenes_Glob[ScenePlus] = [ScenePlus]

        return False

    def __getItemPlus(self, movieName, protoName):
        """ return Movie from ItemPlusData if it exists otherwise creates new """
        ItemPlusData = GroupManager.getGroup("ItemPlusData")

        if ItemPlusData.hasObject(movieName) is True:
            movie = ItemPlusData.getObject(movieName)
        else:
            movie = ItemPlusData.generateObject(movieName, protoName)

        return movie

    def _AddItem(self, itemName):
        itemInManager = ItemManager.getItem(itemName)
        # attach to Item not to slot
        ScenePlus = itemInManager.PlusScene
        if ScenePlus is None:
            return False
        item = itemInManager.getInventoryItem()

        groupName = SceneManager.getSceneMainGroupName(ScenePlus)
        hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(ScenePlus, groupName)

        MovieIdle = self.__getItemPlus("Plus_%s" % itemName, "Movie2_Plus_Passive")
        MovieReady = self.__getItemPlus("PlusReady_%s" % itemName, "Movie2_Plus_Active")
        if any([MovieIdle is None, MovieReady is None]):
            Trace.log("System", 0, "SystemItemPlusScene: unexpected error while creating items in _AddItem: Idle={!r}, Ready={!r}".format(MovieIdle, MovieReady))
            return False

        MovieIdle.setPosition((0, 0))
        MovieIdle.setEnable(False)
        MovieReady.setPosition((0, 0))
        MovieReady.setEnable(False)

        if hasSceneActiveQuest:
            MovieReady.setEnable(True)
            State = "Ready"
        else:
            MovieIdle.setEnable(True)
            State = "Idle"

        PlusItemIndicated = Mengine.getCurrentAccountSettingBool("DifficultyCustomPlusItemIndicated")
        Movie = [MovieIdle, MovieReady, State]
        if PlusItemIndicated is False:
            MovieReady.setEnable(False)
            Movie = [MovieIdle, MovieIdle, State]
        self._AddChieldIt(item, Movie)

        self.items_Inventort[itemName] = [item, Movie, itemInManager, ScenePlus]
        return True

    def _itemRemove(self, item):
        for key, val in self.items_Inventort.iteritems():
            if (val[0] == item):
                self._RemoveChieldIt(val[0], val[1])
                self.items_Inventort.pop(key, None)
                self.items_Inventort_Keys.pop(key)
                return False
        return False

    def _RemChildren(self, Scene):
        if self.hasOpenItemPlus():
            GroupZoom, ScenePlus, ScenePlus_Scene = SystemItemPlusScene.Open_Zoom

            if Scene == ScenePlus_Scene:
                Scenarios = ScenarioManager.getSceneRunScenarios(ScenePlus, ScenePlus)

                Notification.notify(Notificator.onGroupDisable, ScenePlus)

                self._Clear_ScenePlus(GroupZoom)

                for ScenarioRunner in Scenarios:
                    ScenarioRunner.skip()
                    pass

                Notification.notify(Notificator.onSceneLeave, ScenePlus)

                SystemItemPlusScene.Open_Zoom = None

                # print 'ItemPlus Fix Fired'
                pass

        if SceneManager.hasLayerScene(self.ItemPlusInventoryName) is False:
            return False

        for key, val in self.items_Inventort.iteritems():
            self._RemoveChieldIt(val[0], val[1])
        self.items_Inventort = {}  # fix crash

        return False

    def _AddChildren(self, Scene):
        if SceneManager.hasLayerScene(self.ItemPlusInventoryName) is False:
            return False

        for key, val in self.items_Inventort.iteritems():
            self._AddChieldIt(val[0], val[1])

        return False

    def _AddChieldIt(self, item, Movie):
        ItemEnt = item.getEntity()
        mEntNode1 = Movie[0].getEntityNode()
        mEntNode2 = Movie[1].getEntityNode()
        ItemEnt.addChild(mEntNode2)
        ItemEnt.addChild(mEntNode1)

        Center = ItemEnt.getSpriteCenter()

        mEntNode1.setLocalPosition(Center)
        mEntNode2.setLocalPosition(Center)

    def _RemoveChieldIt(self, item, Movie):
        ItemEnt = item.getEntity()
        mEntNode1 = Movie[0].getEntityNode()
        ItemEnt.removeChild(mEntNode1)
        if Movie[0] != Movie[1]:  # todo: check is itemEnt hasChild ... instead of check Movie0!=Movie1
            mEntNode2 = Movie[1].getEntityNode()
            ItemEnt.removeChild(mEntNode2)
            Movie[1].onDestroy()
        Movie[0].onDestroy()

    ##############################################
    def _OpenZoom(self, GroupZoom, ScenePlus):
        if self.hasOpenItemPlus():
            self._CloseZoom()

            return False

        SystemItemPlusScene.Open_Zoom = (GroupZoom, ScenePlus, SceneManager.getCurrentSceneName())
        self._OpenZoomEnd(GroupZoom, ScenePlus)

        return False

    # ////////////////////////////////////////////////
    def _CloseZoom(self, *args):
        self._ItemPlus_Activate()
        if self.hasOpenItemPlus() is False:
            return False

        GroupZoom = SystemItemPlusScene.Open_Zoom[0]
        ScenePlus = SystemItemPlusScene.Open_Zoom[1]

        self._CloseZoomEnd(GroupZoom, ScenePlus, *args)

        SystemItemPlusScene.Open_Zoom = None

        return False

    def _OpenZoomEnd(self, GroupZoom, ScenePlus):
        zom_G = ZoomManager.getZoomOpenGroupName()

        if (zom_G != None):
            # ZoomManager._zoomLeave(zom_G)
            ZoomManager.closeZoom(zom_G)

        Notification.notify(Notificator.onSceneInit, ScenePlus)
        Notification.notify(Notificator.onSceneEnter, ScenePlus)
        if GroupZoom.getEnable() is False:
            GroupZoom.onEnable()
            Notification.notify(Notificator.onGroupEnable, ScenePlus)
        else:
            Trace.log("System", 0, "Something wrong with your item+ {!r} - scene is already activated!!")

        self.tc_Fade = TaskManager.createTaskChain(Repeat=False)

        if GroupZoom.hasObject("Socket_Scene") is True:
            Socket_Scene = GroupZoom.getObject("Socket_Scene")
            Socket_Scene.setBlock(True)
            Socket_Scene.setInteractive(True)

        if SceneManager.hasLayerScene(self.ItemPlusDefaultName) is True:
            TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName=self.ItemPlusDefaultName, Value=True)

            group = GroupManager.getGroup(self.ItemPlusDefaultName)

            with self.tc_Fade as source_open:
                with GuardBlockInput(source_open) as guard_open:
                    with guard_open.addParallelTask(4) as (tc_fade, tc_move, tc_scale, tc_alpha):
                        tc_fade.addTask("AliasFadeIn", FadeGroupName=self.ItemPlusFadeGroup, ReturnItem=False,
                                        To=self.ItemPlusFadeValue, Time=self.ItemPlusOpenFadeTime)

                        tc_move.addFunction(self._posSeter)
                        tc_move.addTask("TaskNodeMoveTo", Node=self.Node_Fade, To=self.posTo,
                                        Time=self.ItemPlusOpenMoveTime)

                        tc_scale.addTask("TaskNodeScaleTo", Node=self.Node_Fade, From=(0.0, 0.0, 1.0),
                                         To=(1.0, 1.0, 1.0), Time=self.ItemPlusOpenScaleTime)

                        tc_alpha.addTask("TaskNodeAlphaTo", Node=self.Node_Fade, From=0.0, To=1.0,
                                         Time=self.ItemPlusOpenAlphaTime)

            self.enableObjects(group)
        else:
            self.enableObjects(GroupZoom)

    def _posSeter(self):
        GroupZoom = SystemItemPlusScene.Open_Zoom[0]
        ScenePlus = SystemItemPlusScene.Open_Zoom[1]
        GroupLayer = GroupZoom.getMainLayer()
        ItemPlusDefaultGroup = GroupManager.getGroup(self.ItemPlusDefaultName)
        ItemPlusDefaultLayer = ItemPlusDefaultGroup.getMainLayer()

        for key in self.items_Inventort:
            for elem in self.items_Inventort[key]:
                if elem == ScenePlus:
                    item = self.items_Inventort[key][0]
                    ItemEnt = item.getEntity()
                    ItemNode = item.getEntityNode()
                    Item_pos = ItemNode.getWorldPosition()
                    Center = ItemEnt.getSpriteCenter()

                    content_movie_name = "Movie2_Content"
                    if ItemPlusDefaultGroup.hasObject(content_movie_name):
                        content_movie = ItemPlusDefaultGroup.getObject(content_movie_name)

                        content_slot_name = "content"
                        if content_movie.hasMovieSlot(content_slot_name):
                            content_node = content_movie.getMovieSlot(content_slot_name)
                        else:
                            content_node = content_movie.getEntityNode()

                            if _DEVELOPMENT:
                                Trace.msg_err("You can add 'slot:%s' in '%s' of '%s' to get more control...",
                                              content_slot_name, content_movie_name, self.ItemPlusDefaultName)

                        content_node.addChild(self.Node_Fade)

                    else:
                        ItemPlusDefaultLayer.addChild(self.Node_Fade)

                    pos_Node_Fade = self.Node_Fade.getWorldPosition()
                    # print "Center",Center
                    # print "Item_pos", Item_pos

                    self.posFrom[0] = Item_pos.x + Center.x / 2
                    self.posFrom[1] = Item_pos.y + Center.y / 2
                    # print "self.posFrom",self.posFrom

                    self.posTo[0] = 0.0
                    self.posTo[1] = 0.0

                    Start_pos = (self.posFrom[0], self.posFrom[1])

                    self.Node_Fade.addChild(GroupLayer)
                    self.Node_Fade.setWorldPosition(Start_pos)
                    return

    def enableObjects(self, group):
        if group.hasObject("Socket_Close") is True:
            Socket_Close = group.getObject("Socket_Close")
            Socket_Close.setBlock(True)
            Socket_Close.setInteractive(True)

            hotspot = Socket_Close.getEntity().getHotSpot()
            hotspot.setEventListener(onHandleMouseButtonEvent=self._CloseZoomHotSpot)
            hotspot.enable()

        if group.hasObject("Socket_Blocker") is True:
            Socket_Block = group.getObject("Socket_Blocker")
            Socket_Block.setBlock(True)
            Socket_Block.setInteractive(True)

        botName = "Movie2Button_Close"
        if group.hasObject(botName) is True:
            Bot_Close = group.getObject(botName)
            nameChain = "ClickButton_ItemPlus_CloseZoom"
            if TaskManager.existTaskChain(nameChain):
                TaskManager.cancelTaskChain(nameChain)

            with TaskManager.createTaskChain(Name=nameChain, Group=group, Repeat=True) as tc:
                tc.addTask("TaskMovie2ButtonClick", Movie2ButtonName=botName)
                tc.addNotify(Notificator.onItemZoomLeaveOpenZoom)

    def _CloseZoomHotSpot(self, context, event):
        if event.isDown is False:
            return False

        Notification.notify(Notificator.onItemZoomLeaveOpenZoom)

        return True

    def _CloseZoomEnd(self, GroupZoom, ScenePlus, point=None, b_remove_from_inv=False, b_point_to_bezier=False, time=None):
        Notification.notify(Notificator.onGroupDisable, ScenePlus)

        if SceneManager.hasLayerScene(self.ItemPlusDefaultName) is False:
            return

        Scenarios = ScenarioManager.getSceneRunScenarios(ScenePlus, ScenePlus)

        if point is None:
            point = self.posFrom

        if b_point_to_bezier:
            task_node_move_to = "TaskNodeBezier2To"
        else:
            task_node_move_to = "TaskNodeMoveTo"

        if time is None:
            fade_time = self.ItemPlusCloseFadeTime
            move_tome = self.ItemPlusCloseMoveTime
            scale_time = self.ItemPlusCloseScaleTime
            alpha_time = self.ItemPlusCloseAlphaTime
            alpha_delay = self.ItemPlusCloseAlphaDelay
        else:
            fade_time = time
            move_tome = time
            scale_time = time
            alpha_time = time * 0.33
            alpha_delay = time * 0.66

        self.tc_Fade_close = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Fade_close as source_close:
            with GuardBlockInput(source_close) as guard_close:
                # close effect
                with guard_close.addParallelTask(4) as (tc_fade, tc_move, tc_scale, tc_alpha):
                    tc_fade.addTask("AliasFadeOut", FadeGroupName=self.ItemPlusFadeGroup, Time=fade_time, From=self.ItemPlusFadeValue)

                    tc_move.addTask(task_node_move_to, Node=self.Node_Fade, To=point, Time=move_tome)

                    tc_scale.addTask("TaskNodeScaleTo", Node=self.Node_Fade, To=(0.0, 0.0, 1.0), Time=scale_time)

                    tc_alpha.addDelay(alpha_delay)
                    tc_alpha.addTask("TaskNodeAlphaTo", Node=self.Node_Fade, To=0.0, Time=alpha_time)

                if b_remove_from_inv:  # remove from inventory
                    guard_close.addScope(self.remove_from_inventory, ScenePlus)
                    guard_close.addFunction(self._Clear_ScenePlus, GroupZoom)

                else:  # if no remove item from inventory, then clean itemPlus
                    for ScenarioRunner in Scenarios:
                        guard_close.addFunction(ScenarioRunner.skip)

                    guard_close.addFunction(self._Clear_ScenePlus, GroupZoom)

                guard_close.addNotify(Notificator.onSceneLeave, ScenePlus)

    def remove_from_inventory(self, source, ScenePlus):
        Item = ItemManager.findItemByScenePlus(ScenePlus)

        if Item is not None:
            Inventory = DemonManager.getDemon(self.ItemPlusInventoryName)
            InventoryItem = Item.getInventoryItem()
            source.addTask("AliasInventoryRemoveInventoryItem", Inventory=Inventory, InventoryItem=InventoryItem)
        else:
            msg = 'SystemItemPlus::remove_from_inventory(), RemoveItemPlusOnClose=True ItemManager' \
                  ' can\'t find item with "%s" PlusScene name' % ScenePlus
            Trace.log("System", 0, msg)

    def _Clear_ScenePlus(self, GroupZoom):
        self.posTo = [0.0, 0.0]
        self.posFrom = [0.0, 0.0]

        if GroupZoom is not None:
            GroupLayer = GroupZoom.getMainLayer()
            # print " --- Item+ --- GroupZoom={!r} parent='{}' | Fade='{}' | layer={!r} parent='{}'".format(
            #     GroupZoom.getName(), GroupZoom.getParent().getName() if GroupZoom.getParent() else None,
            #     self.Node_Fade.getName(), GroupLayer.getName(),
            #     GroupLayer.getParent().getName() if GroupLayer.getParent() else None)
            if GroupLayer.getParent() == self.Node_Fade:
                self.Node_Fade.removeChild(GroupLayer)
                GroupZoom.onDisable()

        ItemPlusDefaultGroup = GroupManager.getGroup(self.ItemPlusDefaultName)

        content_movie_name = "Movie2_Content"
        if ItemPlusDefaultGroup.hasObject(content_movie_name):
            content_movie = ItemPlusDefaultGroup.getObject(content_movie_name)

            content_slot_name = "content"
            if content_movie.hasMovieSlot(content_slot_name):
                content_node = content_movie.getMovieSlot(content_slot_name)
            else:
                content_node = content_movie.getEntityNode()

            content_node.removeChild(self.Node_Fade)

        else:
            ItemPlusDefaultLayer = ItemPlusDefaultGroup.getMainLayer()
            ItemPlusDefaultLayer.removeChild(self.Node_Fade)

        if SceneManager.hasLayerScene(self.ItemPlusDefaultName) is True:
            TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName=self.ItemPlusDefaultName, Value=False)

    def _onStop(self):
        for items in self.items_Inventort.itervalues():
            item, Movie, itemInManager, ScenePlus = items
            Movie[0].onDestroy()
            Movie[1].onDestroy()
            Movie = None

        self.items_Inventort = {}
        self.items_Inventort_Keys = {}
        self.items_Scenes_Glob = {}

        if self.tc_Fade != None:
            self.tc_Fade.cancel()
            self.tc_Fade = None

        if self.tc_Fade_close != None:
            self.tc_Fade_close.cancel()
            self.tc_Fade_close = None

    def __CanseltTaskChain(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)

    def _onSave(self):
        save = (self.items_Inventort_Keys, self.items_Scenes_Glob)
        return save

    def _onLoad(self, data_save):
        self.items_Inventort_Keys, self.items_Scenes_Glob = data_save
