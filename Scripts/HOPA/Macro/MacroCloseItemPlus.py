from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Object.ObjectPoint import ObjectPoint
from Foundation.SystemManager import SystemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroCloseItemPlus(MacroCommand):
    def _onValues(self, values):
        self.point = None
        self.b_point_is_tuple = False

        self.b_remove_from_inv = False
        self.b_point_bezier_to = False
        self.override_close_time = None

        if len(values) > 0:
            self.b_remove_from_inv = bool(values[0])

        if len(values) > 1:
            parsed_floats = []
            for i in values[1].split(", "):
                try:
                    val = float(i)
                    parsed_floats.append(val)
                except ValueError:
                    break

            b_is_point_tuple_valid = len(parsed_floats) >= 2 and isinstance(parsed_floats[0], float) and isinstance(parsed_floats[1], float)

            if b_is_point_tuple_valid:  # from point should be tuple
                self.b_point_is_tuple = True
                self.point = (parsed_floats[0], parsed_floats[1])

            else:
                self.point = values[1]  # from point should be type of ObjectPoint

        if len(values) > 2:
            self.b_point_bezier_to = bool(values[2])

        if len(values) > 3:
            self.override_close_time = float(values[3])

    def _onInitialize(self, *args, **kwds):
        # initialize self.point if it's ObjectPoint instance and not tuple(float_x, float_y)
        if self.point is not None and not self.b_point_is_tuple:
            if _DEVELOPMENT is True:
                if GroupManager.hasObject(self.GroupName, self.point) is False:
                    msg = "Not found point {} in group {}. Point should be tuple(float_x, float_y) or ObjectPoint instance"
                    msg = msg.format(self.point, self.GroupName)
                    self.initializeFailed(msg)
                    return
                pass

            point_instance = GroupManager.getObject(self.GroupName, self.point)

            if _DEVELOPMENT is True:
                if not isinstance(point_instance, ObjectPoint):
                    msg = "Not found point {} in group {}. Point should be tuple(float_x, float_y) or ObjectPoint instance"
                    msg = msg.format(self.point, self.GroupName)
                    self.initializeFailed(msg)
                    return
                pass

            self.point = point_instance.getPosition()

    def scopeCloseItemPlus(self, source):
        SystemItemPlusScene = SystemManager.getSystem("SystemItemPlusScene")
        if SystemItemPlusScene.hasOpenItemPlus() is False:
            if _DEVELOPMENT is True:
                Trace.log("Macro", 0, "MacroCloseItemPlus {} invalid, no item plus are open".format(self.GroupName))
            if self.b_remove_from_inv is True:
                source.addScope(SystemItemPlusScene.remove_from_inventory, self.GroupName)
            else:
                source.addDummy()
            return

        item_plus_scene_name = SystemItemPlusScene.Open_Zoom[1]

        with source.addParallelTask(2) as (source_notify, source_observe):
            source_observe.addListener(Notificator.onSceneLeave, Filter=lambda scene_name: scene_name == item_plus_scene_name)

            source_notify.addNotify(Notificator.onItemZoomLeaveOpenZoom, self.point, self.b_remove_from_inv, self.b_point_bezier_to, self.override_close_time)

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "CloseZoom", SceneName=self.SceneName, GroupName=self.GroupName)

        with Quest as tc_quest:
            tc_quest.addScope(self.scopeCloseItemPlus)
