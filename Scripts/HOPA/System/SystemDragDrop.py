from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

ZOOM_MG_FRAME_GROUP = "ZoomMiniMGCountDefault"
ZOOM_COUNTER_DEMON_OBJECT = "Demon_HOGInventoryCount"
ZOOM_DEFAULT_FRAME_GROUP = "ZoomDefault"

SCENE_MG_INVENTORY_GROUP = "MahjongInventory"
SCENE_COUNTER_DEMON_OBJECT = "Demon_MahjongInventory"
SCENE_DEFAULT_INVENTORY_GROUP = "Inventory"

TEXT_NAME = "Text_Message"

SYSTEM_INVENTORY_PANEL = "SystemInventoryPanel"

# todo: other drag drops, which are after macro DragDropCounter Disable, shouldn't processed


class DragDropItem(object):
    def __init__(self, name, is_found=False):
        self.name = name
        self.__is_found = is_found

    def getSerialized(self):
        return [self.name, self.__is_found]

    def setFound(self, bool_):
        self.__is_found = bool_

    def isFound(self):
        return self.__is_found

class DragDropMG(object):
    def __init__(self, group_name):
        self.group_name = group_name
        self.text_id = str()
        self.is_zoom = bool()
        self.drag_drop_items = dict()

        self.is_manual = False
        self.manual_item_count = 0
        self.manual_complete_item_count = 0

    def getSerialized(self):
        items_serialized = [item.getSerialized() for item in self.drag_drop_items.values()]
        return [self.is_zoom, self.text_id, self.is_manual, self.manual_item_count, self.manual_complete_item_count, items_serialized]

    def restore(self, serialized):
        self.is_zoom = serialized[0]
        self.text_id = serialized[1]
        self.is_manual = serialized[2]
        self.manual_item_count = serialized[3]
        self.manual_complete_item_count = serialized[4]

        for item_serialized in serialized[5]:
            drag_drop_item = DragDropItem(*item_serialized)
            self.drag_drop_items[drag_drop_item.name] = drag_drop_item

    def getDragDropItem(self, item_name):
        return self.drag_drop_items.get(item_name)

    def addDragDropItem(self, item_name, is_manual):
        if self.is_manual != is_manual:
            return

        if is_manual:
            item_name = self.manual_item_count
            self.manual_item_count += 1

        if self.drag_drop_items.get(item_name) is None:
            drag_drop_item = DragDropItem(item_name)
            self.drag_drop_items[item_name] = drag_drop_item

    def getDragDropItemNames(self, found_only=False):
        if found_only:
            founded_item_names = list()
            for drag_drop_item in self.drag_drop_items.values():
                if drag_drop_item.isFound():
                    founded_item_names.append(drag_drop_item.name)
            return founded_item_names
        else:
            return [drag_drop_item.name for drag_drop_item in self.drag_drop_items.values()]

class SystemDragDrop(System):
    s_group_drag_drop_mgs = dict()

    def _onRun(self):
        SystemDragDrop.s_group_drag_drop_mgs = {}

        self.addObserver(Notificator.onHOGDragDropMGInit, self.__cbDragDropCounterMGInit)
        self.addObserver(Notificator.onHOGDragDropCounterFrameSwitch, self.__cbDragDropCounterFrameResolve)

        self.addObserver(Notificator.onDragDropItemCreate, self.__cbCreateDragDropItem)
        self.addObserver(Notificator.onDragDropItemComplete, self.__cbDragDropItemComplete)

        self.addObserver(Notificator.onSceneInit, self.__cbDragDropRestore)
        self.addObserver(Notificator.onZoomInit, self.__cbDragDropRestore)

        self.addObserver(Notificator.onHOGDragDropUpdateText, self.__cbDragDropUpdateText)
        return True

    @staticmethod
    def _onSave():
        save_data = dict()
        for group_name, drag_drop_mg in SystemDragDrop.s_group_drag_drop_mgs.iteritems():
            save_data[group_name] = drag_drop_mg.getSerialized()
        return save_data

    @staticmethod
    def _onLoad(save_data):
        for group_name, drag_drop_mg_serialized in save_data.items():
            drag_drop_mg = DragDropMG(group_name)
            drag_drop_mg.restore(drag_drop_mg_serialized)
            SystemDragDrop.s_group_drag_drop_mgs[group_name] = drag_drop_mg

            if drag_drop_mg_serialized[0]:
                zoom = ZoomManager.getZoom(group_name)
                zoom.tempFrameGroupName = ZOOM_MG_FRAME_GROUP

    @staticmethod
    def addDragDropMG(group_name, is_zoom, text_id, is_manual, init_count):
        drag_drop_mg = DragDropMG(group_name)
        drag_drop_mg.is_zoom = is_zoom
        drag_drop_mg.text_id = text_id
        drag_drop_mg.is_manual = is_manual

        if is_manual:
            for i in range(init_count):
                drag_drop_mg.addDragDropItem(str(), is_manual)

        SystemDragDrop.s_group_drag_drop_mgs[group_name] = drag_drop_mg

    @staticmethod
    def getDragDropMG(group_name):
        return SystemDragDrop.s_group_drag_drop_mgs.get(group_name)

    @staticmethod
    def removeDragDropMG(group_name):
        SystemDragDrop.s_group_drag_drop_mgs.pop(group_name)

    @staticmethod
    def updateInventoryPanel(group_name):
        drag_drop_mg = SystemDragDrop.getDragDropMG(group_name)

        if drag_drop_mg is not None:
            if drag_drop_mg.is_zoom:
                group = GroupManager.getGroup(ZOOM_MG_FRAME_GROUP)
                object_ = group.getObject(ZOOM_COUNTER_DEMON_OBJECT)

            else:
                group = GroupManager.getGroup(SCENE_MG_INVENTORY_GROUP)
                object_ = group.getObject(SCENE_COUNTER_DEMON_OBJECT)

            found_items = drag_drop_mg.getDragDropItemNames(found_only=True)
            all_items = drag_drop_mg.getDragDropItemNames(found_only=False)

            object_.setParam("TextID", drag_drop_mg.text_id)
            object_.setParam("FoundItems", found_items)
            object_.setParam("ItemsCount", len(all_items))

    @staticmethod
    def __cbCreateDragDropItem(group_name, item_name, is_manual):
        drag_drop_mg = SystemDragDrop.getDragDropMG(group_name)

        if drag_drop_mg is not None:
            drag_drop_mg.addDragDropItem(item_name, is_manual)

            if is_manual:
                SystemDragDrop.updateInventoryPanel(group_name)  # update item counter and inventory text on fly

        return False

    @staticmethod
    def __cbDragDropItemComplete(group_name, item_name, is_manual):
        drag_drop_mg = SystemDragDrop.getDragDropMG(group_name)

        if drag_drop_mg is not None:
            if drag_drop_mg.is_zoom:
                group = GroupManager.getGroup(ZOOM_MG_FRAME_GROUP)
                object_ = group.getObject(ZOOM_COUNTER_DEMON_OBJECT)

            else:
                group = GroupManager.getGroup(SCENE_MG_INVENTORY_GROUP)
                object_ = group.getObject(SCENE_COUNTER_DEMON_OBJECT)

            if drag_drop_mg.is_manual != is_manual:
                return False

            if is_manual:
                item_name = drag_drop_mg.manual_complete_item_count
                drag_drop_mg.manual_complete_item_count += 1

            object_.appendParam("FoundItems", item_name)

            drag_drop_item = drag_drop_mg.getDragDropItem(item_name)
            drag_drop_item.setFound(True)

        return False

    @staticmethod
    def __cbDragDropUpdateText(group_name, text_id, text_alpha):
        drag_drop_mg = SystemDragDrop.getDragDropMG(group_name)

        drag_drop_mg.text_id = text_id

        if drag_drop_mg.is_zoom:
            inv_panel_demon = GroupManager.getGroup(ZOOM_MG_FRAME_GROUP).getObject(ZOOM_COUNTER_DEMON_OBJECT)
            text = inv_panel_demon.getObject(TEXT_NAME)

        else:
            inv_panel_demon = GroupManager.getGroup(SCENE_MG_INVENTORY_GROUP).getObject(SCENE_COUNTER_DEMON_OBJECT)
            text = inv_panel_demon.getObject(TEXT_NAME)

        if text_alpha == 0.0:
            inv_panel_demon.setParam("TextID", text_id)

        else:
            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskNodeAlphaTo", Node=text.getEntityNode(), To=0.0, Time=text_alpha)
                tc.addFunction(inv_panel_demon.setParam, "TextID", text_id)
                tc.addTask("TaskNodeAlphaTo", Node=text.getEntityNode(), To=1.0, Time=text_alpha)

        return False

    @staticmethod
    def __cbDragDropRestore(group_name):
        SystemDragDrop.updateInventoryPanel(group_name)

        return False

    @staticmethod
    def __cbDragDropCounterMGInit(group_name, text_id, is_manual, init_count):
        if SystemDragDrop.getDragDropMG(group_name) is None:
            is_zoom = ZoomManager.hasZoom(group_name)
            SystemDragDrop.addDragDropMG(group_name, is_zoom, text_id, is_manual, init_count)
        return False

    @staticmethod
    def __cbDragDropCounterFrameResolve(group_name, state):
        is_zoom = ZoomManager.hasZoom(group_name)

        if state == 'Enable':
            if is_zoom:
                zoom = ZoomManager.getZoom(group_name)
                Notification.notify(Notificator.onZoomEnigmaChangeFrameGroup, ZOOM_MG_FRAME_GROUP)
                zoom.tempFrameGroupName = ZOOM_MG_FRAME_GROUP
            else:
                Notification.notify(Notificator.onInventoryChage, SCENE_MG_INVENTORY_GROUP)
            SystemDragDrop.updateInventoryPanel(group_name)
        else:
            if is_zoom:
                zoom = ZoomManager.getZoom(group_name)
                zoom.tempFrameGroupName = None
                Notification.notify(Notificator.onZoomEnigmaChangeBackFrameGroup)
            else:
                Notification.notify(Notificator.onInventoryChage, SCENE_DEFAULT_INVENTORY_GROUP)
                sys = SystemManager.getSystem(SYSTEM_INVENTORY_PANEL)
                sys.CurrentInventory = SCENE_DEFAULT_INVENTORY_GROUP

            if SystemDragDrop.getDragDropMG(group_name) is not None:
                SystemDragDrop.removeDragDropMG(group_name)
        return False