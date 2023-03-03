from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ZoomManager import ZoomManager


class MacroZoomUpdatePolygon(MacroCommand):

    def _onValues(self, values):
        self.ZoomName = values[0]

        if values[1].startswith("("):
            self.Points = []
            points = values[1:]
            for point in points:
                pair = tuple(map(lambda x: float(x), point[1:-1].split(", ")))
                self.Points.append(pair)
            self.ReferObjectName = None
        else:
            self.ReferObjectName = values[1]
            self.Points = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SceneManager.hasSceneZoom(self.SceneName, self.ZoomName) is False:
                self.initializeFailed("Scene '%s' not found zoom '%s'" % (self.SceneName, self.ZoomName))

            if self.ReferObjectName is not None:
                if GroupManager.hasObject(self.GroupName, self.ReferObjectName) is False:
                    self.initializeFailed("Scene '%s' Group '%s' not found object '%s'" % (
                        self.SceneName, self.GroupName, self.ReferObjectName))
                refer_object = GroupManager.getObject(self.GroupName, self.ReferObjectName)
                if refer_object.hasParam("Polygon") is False:
                    self.initializeFailed("Scene '%s' Group '%s' ReferObject '%s' hasn't param Polygon!" % (
                        self.SceneName, self.GroupName, self.ReferObjectName))
                else:
                    polygon = refer_object.getParam("Polygon") or []
                    if len(polygon) < 3:
                        self.initializeFailed("Scene '%s' Group '%s' ReferObject '%s' should have at least 3 points!" % (
                            self.SceneName, self.GroupName, self.ReferObjectName))

            if self.Points is None and self.ReferObjectName is None:
                self.initializeFailed("You should init or Points, or ReferObjectName to use this macro command")

    def _updatePolygon(self):
        Zoom = ZoomManager.getZoom(self.ZoomName)
        ObjectZoom = Zoom.object

        if self.Points is not None:
            points = self.Points
        else:
            refer_object = GroupManager.getObject(self.GroupName, self.ReferObjectName)
            points = refer_object.getParam("Polygon")

        # print "Zoom", self.ZoomName, "set Polygon to", points
        ObjectZoom.setParam("Polygon", points)

    def _onGenerate(self, source):
        source.addFunction(self._updatePolygon)
