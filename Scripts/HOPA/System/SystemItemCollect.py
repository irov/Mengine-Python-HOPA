from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ItemCollectManager import ItemCollectManager


class ItemParams(object):
    def __init__(self, params):
        self.Item = params.Item
        self.Idle = params.Idle
        self.Silhouette = params.Silhouette
        self.AllowedItems = params.AllowedItems

        self.Idle.setEnable(False)
        self.Item.setEnable(True)
        self.Silhouette.setEnable(True)

        self.ItemPosition = None

    def switchIcon(self, value):
        self.Idle.setEnable(value)
        self.Item.setEnable(not value)
        self.Silhouette.setEnable(not value)


class SystemItemCollect(System):
    s_item_collects = {}
    s_found_items = {}
    s_item_lists = {}
    s_CurrentOpenItemCollect = None

    def _onRun(self):
        SystemItemCollect.s_item_collects = {}
        SystemItemCollect.s_found_items = {}
        SystemItemCollect.s_item_lists = {}
        SystemItemCollect.s_CurrentOpenItemCollect = None

        item_collect_params = ItemCollectManager.getItemCollectParams()
        self.__createItem(item_collect_params)

        self.__runObservers()
        return True

    def __runObservers(self):
        self.addObserver(Notificator.onItemCollectInit, self.__onItemCollectInit)
        self.addObserver(Notificator.onFinishItemCollect, self.__FinishItemCollect)
        self.addObserver(Notificator.onZoomClick, self.__onSocketClick)
        self.addObserver(Notificator.onTransitionClick, self.__onSocketClick)
        self.addObserver(Notificator.onSocketClick, self.__onSocketClick)
        self.addObserver(Notificator.onItemClick, self.__onItemClick)
        self.addObserver(Notificator.onCloseCurrentItemCollect, self.__onSocketClick, None)
        self.addObserver(Notificator.onSceneDeactivate, self.__onSceneDeactivate)

    def __createItem(self, item_collect_params):
        for item_name in item_collect_params:
            params = item_collect_params[item_name]
            item_params = ItemParams(params)
            SystemItemCollect.s_item_collects[item_name] = item_params

    @staticmethod
    def getItemCollects():
        return SystemItemCollect.s_item_collects

    @staticmethod
    def getItemCollect(item_name):
        return SystemItemCollect.s_item_collects.get(item_name)

    @staticmethod
    def addFoundItem(item_name):
        item = SystemItemCollect.getItemCollect(item_name)
        SystemItemCollect.s_found_items[item_name] = item

    @staticmethod
    def hasFoundItem(item_name):
        return item_name in SystemItemCollect.s_found_items

    @staticmethod
    def getItemList():
        return SystemItemCollect.s_item_lists

    @staticmethod
    def getCurrentItemCollect():
        return SystemItemCollect.s_CurrentOpenItemCollect

    def __onSceneDeactivate(self, scene_name):
        if self.hasOpenItemCollect() is True:
            self.setCurrentOpenItemCollect(None)
        return False

    def __onItemClick(self, itemObject):
        Demon = DemonManager.getDemon('ItemCollect')

        if Demon.isActive() is False or Demon.getEnable() is False:
            return False

        if SystemItemCollect.hasOpenItemCollect() is False:
            return False

        checkList = SystemItemCollect.s_item_lists[SystemItemCollect.s_CurrentOpenItemCollect][0]
        if itemObject.getName() in checkList:
            return False

        with TaskManager.createTaskChain() as source:
            source.addScope(Demon.scopePlaySceneEffect, False)
            source.addTask('TaskSceneLayerGroupEnable', LayerName='ItemCollect', Value=False)
            source.addFunction(self.setCurrentOpenItemCollect, None)
        return False

    def __onSocketClick(self, value):
        Demon = DemonManager.getDemon('ItemCollect')

        if Demon.isActive() is False or Demon.getEnable() is False:
            return False

        if Demon.getOpeningProcessProgress() is True:
            return False

        SceneName = SceneManager.getCurrentSceneName()
        SocketName = None
        if value is not None:
            SocketName = value.getName()
            if value.getName() is 'Socket_Click':
                return False

        Demon.cancelTaskChain()

        if SystemItemCollect.hasOpenItemCollect() is True:
            SceneName, SocketName = SystemItemCollect.s_CurrentOpenItemCollect
        Notification.notify(Notificator.onHintActionItemCollectEnd)

        def changeItemCollectState(source, flag):
            """
            :param flag: True for open, False for close
            """
            source.addScope(Demon.scopePlaySceneEffect, flag)
            source.addTask('TaskSceneLayerGroupEnable', LayerName='ItemCollect', Value=flag)
            source.addFunction(self.setCurrentOpenItemCollect, None)

        if (SceneName, SocketName) in SystemItemCollect.s_item_lists.keys():
            with TaskManager.createTaskChain() as source:
                with source.addIfTask(SystemItemCollect.hasOpenItemCollect) as (tc_true, tc_false):
                    tc_true.addScope(changeItemCollectState, False)
        return False

    def __FinishItemCollect(self, SceneName, Socket, flag):
        Demon = DemonManager.getDemon('ItemCollect')
        if Demon.isActive() is False or Demon.getEnable() is False:
            return False

        SocketName = Socket.getName()
        items_list = []
        socket = None

        if (SceneName, SocketName) in SystemItemCollect.s_item_lists:
            items_list = SystemItemCollect.s_item_lists[SceneName, SocketName][0]
            socket = SystemItemCollect.s_item_lists[SceneName, SocketName][1]
            SystemItemCollect.s_item_lists[SceneName, SocketName][2] = True

        with TaskManager.createTaskChain() as source:
            source.addFunction(self.setCurrentOpenItemCollect, None)
            source.addScope(Demon.scopePlaySceneEffect, False)
            source.addTask('TaskSceneLayerGroupEnable', LayerName='ItemCollect', Value=False)
            if flag is True:
                source.addNotify(Notificator.onItemCollectComplete, socket, items_list)
                if TaskManager.existTaskChain('ItemCollectSystem_{}_{}'.format(SceneName, SocketName)):
                    TaskManager.cancelTaskChain('ItemCollectSystem_{}_{}'.format(SceneName, SocketName))

        return False

    def __onItemCollectInit(self, socket, items_list, SceneName, SocketName):
        """ Observer on MacroItemCollect - setup params for ItemCollect (starts it) """

        Demon = DemonManager.getDemon('ItemCollect')
        if Demon.isActive() is False:
            return False

        SystemItemCollect.s_item_lists[(SceneName, SocketName)] = [items_list, socket, False]
        self.__start_item_collect(SceneName, SocketName)

        return False

    def calcPosition(self, socket):
        """ returns center world position of inputted socket """

        socket_entity = socket.getEntity()
        hotspot = socket_entity.getHotSpot()
        position = hotspot.getWorldPolygonCenter()

        return position

    def __start_item_collect(self, SceneName, SocketName):
        """ Runs TaskChain that handle item click """

        ItemHolder = Holder()
        items_list = SystemItemCollect.s_item_lists.get((SceneName, SocketName))[0]
        socket = SystemItemCollect.s_item_lists.get((SceneName, SocketName))[1]
        Demon = DemonManager.getDemon('ItemCollect')

        TaskChainName = 'ItemCollectSystem_{}_{}'.format(SceneName, SocketName)
        if TaskManager.existTaskChain(TaskChainName) is True:
            TaskManager.cancelTaskChain(TaskChainName)

        with TaskManager.createTaskChain(Name=TaskChainName, Repeat=True) as source:
            source.addFunction(ItemHolder.set, None)
            with source.addRaceTask(2) as (ItemClick, SocketClick):
                SocketClick.addTask('TaskSocketClick', Socket=socket)

                for ItemName, raceItemClick in ItemClick.addRaceTaskList(items_list):
                    item_collect = SystemItemCollect.getItemCollect(ItemName)
                    raceItemClick.addTask('TaskItemClick', Item=item_collect.Item)
                    raceItemClick.addFunction(Demon.setParam, 'AttachItem', ItemName)
                    raceItemClick.addFunction(ItemHolder.set, item_collect.Item)

            with source.addIfTask(SystemItemCollect.hasOpenItemCollect) as (tc_true, tc_false):
                socket_center_position = self.calcPosition(socket)
                position = (socket_center_position.x, socket_center_position.y, 0.0)

                tc_false.addFunction(Demon.setParams, ItemsList=items_list, ItemCollectArea=socket, Position=position)
                tc_false.addFunction(SystemItemCollect.setCurrentOpenItemCollect, (SceneName, SocketName))
                tc_false.addTask('TaskSceneLayerGroupEnable', LayerName='ItemCollect', Value=True)
                tc_false.addScope(self.scopeItemAttach, ItemHolder, Demon)

                tc_true.addFunction(Demon.setParam, 'AttachItem', None)

    def scopeItemAttach(self, source, holder, Demon):
        item = holder.get()

        if item is None:
            return

        OffsetValue = DefaultManager.getDefaultTuple("ItemCollectAttachOffset", (0, 0), valueType=int, divider=", ")

        source.addTask('TaskSceneLayerGroupEnable', LayerName='ItemCollect', Value=True)
        source.addFunction(Demon.playItemSelectEffect, item)
        source.addTask("TaskFanItemInHand", FanItem=item)
        source.addTask("TaskArrowAttach", OffsetValue=OffsetValue, Origin=True, Object=item, MovieAttach=True,
                       AddArrowChild=Mengine.hasTouchpad() is False)
        source.addFunction(Demon.setParam, 'PreAttach', item)

    @staticmethod
    def setCurrentOpenItemCollect(value):
        SystemItemCollect.s_CurrentOpenItemCollect = value

    @staticmethod
    def hasOpenItemCollect():
        hasOpenItemCollect = SystemItemCollect.s_CurrentOpenItemCollect is not None
        return hasOpenItemCollect

    def _onStop(self):
        for (SceneName, SocketName) in SystemItemCollect.s_item_lists:
            if TaskManager.existTaskChain('ItemCollectSystem_{}_{}'.format(SceneName, SocketName)):
                TaskManager.cancelTaskChain('ItemCollectSystem_{}_{}'.format(SceneName, SocketName))

    @classmethod
    def _onSave(cls):
        save_data = {'FoundItems': [], 'ItemLists': {}}
        for item_name in cls.s_found_items:
            save_data['FoundItems'].append(item_name)

        for (SceneName, SocketName), (item_list, _, flag) in cls.s_item_lists.iteritems():
            save_data['ItemLists'][(SceneName, SocketName)] = item_list, SocketName, flag

        return save_data

    @classmethod
    def _onLoad(cls, save_data):
        for item_name, item in cls.s_item_collects.iteritems():
            if item_name in save_data['FoundItems']:
                cls.addFoundItem(item_name)
                item.switchIcon(True)
            else:
                item.switchIcon(False)

        for (SceneName, SocketName), (item_list, SocketName, flag) in save_data['ItemLists'].iteritems():
            if flag is True:
                Notification.notify(Notificator.onAccountFinalize, SocketName, item_list)
            socket = GroupManager.getObject(SceneName, SocketName)
            cls.s_item_lists[(SceneName, SocketName)] = [item_list, socket, flag]
