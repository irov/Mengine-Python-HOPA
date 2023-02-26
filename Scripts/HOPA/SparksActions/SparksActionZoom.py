from Foundation.Task.MixinObjectTemplate import MixinZoom
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault
from HOPA.ZoomManager import ZoomManager

class SparksActionZoom(SparksActionDefault, MixinZoom):
    def _onParams(self, params):
        super(SparksActionZoom, self)._onParams(params)
        pass

    def _getSparksObject(self):
        return self.Zoom
        pass

    def _getSparksPosition(self, zoom):
        zoomEntity = zoom.getEntity()

        HotSpot = zoomEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    def _onCheck(self):
        Enable = self.Zoom.getParam("Enable")
        if Enable is False:
            return False

        ZoomGroupName = ZoomManager.getZoomGroupName(self.Zoom)
        zoom = ZoomManager.getZoom(ZoomGroupName)
        Open = zoom.getOpen()
        if Open is True:
            return False
            pass

        BlockOpen = self.Zoom.getParam("BlockOpen")
        if BlockOpen is True:
            return False
            pass

        return True
        pass

    def _changeEmmiterForm(self, effectObject):
        polygon = self.Zoom.getPolygon()

        Point = self.polygon_center(polygon)
        # print "polygon_center",Point,"PointNot",

        if effectObject.hasMovieNode("spark") is False:
            return False
            pass

        effectObject.setPosition(Point)

        spark = effectObject.getMovieNode("spark")

        # spark.setEmitterPosition((0, 0))
        spark.setEmitterPositionRelative(True)
        spark.setEmitterRandomMode(True)
        # spark.setEmitterPolygon(polygon)
        # spark.changeEmitterPolygon(polygon)

        return True
        pass

    def polygon_center(self, Poligon):
        maxX, maxY = -1000, -1000
        minX, minY = 9999999, 999999
        for elem in Poligon:
            if elem[0] > maxX:
                maxX = elem[0]

            if elem[0] < minX:
                minX = elem[0]

            if elem[1] > maxY:
                maxY = elem[1]

            if elem[1] < minY:
                minY = elem[1]
        x = (maxX + minX) / 2
        y = (maxY + minY) / 2
        center = (x, y)
        return center

    pass