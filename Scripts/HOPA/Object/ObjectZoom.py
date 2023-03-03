from Foundation.Object.Object import Object


class ObjectZoom(Object):
    PARAMS_Interactive = 1

    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.addParam(Type, "Polygon")
        Type.addConst(Type, "HintPoint")
        Type.addParam(Type, "Point")
        Type.addParam(Type, "BlockOpen")
        Type.addParam(Type, "End")
        pass

    def _onParams(self, params):
        super(ObjectZoom, self)._onParams(params)

        # self.initParam("ZoomGroupName", params, None)

        self.initParam("Polygon", params)
        self.initConst("HintPoint", params, None)

        self.initParam("Point", params, None)
        self.initParam("BlockOpen", params, False)

        self.initParam("End", params, False)
        pass

    def _onInitialize(self):
        super(ObjectZoom, self)._onInitialize()

        if _DEVELOPMENT is True:
            HintPoint = self.getHintPoint()
            if HintPoint is not None:
                if isinstance(HintPoint, tuple) is False or len(HintPoint) != 2:
                    self.initializeFailed("'%s' invalid initialize, incorrect param HintPoint" % (self.getName()))

                Polygon = self.getPolygon()
                if Mengine.isPointInsidePolygon(HintPoint, Polygon) is False:
                    self.initializeFailed("'%s' invalid initialize, HintPoint %s must be inside polygon %s" % (
                    self.getName(), HintPoint, Polygon))

    def calcWorldHintPoint(self):
        hintPoint = self.getHintPoint()

        if hintPoint is not None:
            groupScene = self.getGroup()
            slot = groupScene.getScene()
            posScene = slot.getLocalPosition()

            return posScene.x + hintPoint[0], posScene.y + hintPoint[1]

        if self.isActive():
            hotspot = self.entity.getHotSpot()

            if hotspot is not None:
                if hotspot.__class__.__name__ == "HotSpotPolygon":
                    return hotspot.getWorldPolygonCenter()

                elif hotspot.__class__.__name__ == "HotSpotImage":
                    pos = hotspot.getWorldPosition()

                    pos.x += hotspot.getWidth() >> 1
                    pos.y += hotspot.getHeight() >> 1

                    return pos
