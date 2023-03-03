from Foundation.Object.DemonObject import DemonObject


class ObjectTransition(DemonObject):
    PARAMS_Interactive = 1

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addConst(Type, "Polygon")
        Type.addConst(Type, "HintPoint")
        Type.addParam(Type, "BlockOpen")
        pass

    def _onParams(self, params):
        super(ObjectTransition, self)._onParams(params)

        self.initConst("Polygon", params)
        self.initConst("HintPoint", params, None)
        self.initParam("BlockOpen", params, False)
        pass

    def _onInitialize(self):
        super(ObjectTransition, self)._onInitialize()

        if _DEVELOPMENT is True:
            HintPoint = self.getHintPoint()
            if HintPoint is not None:
                if isinstance(HintPoint, tuple) is False or len(HintPoint) != 2:
                    self.initializeFailed("'%s' invalid initialize, incorrect param HintPoint '%s'" % (self.getName(), HintPoint))

                Polygon = self.getPolygon()
                if Mengine.isPointInsidePolygon(HintPoint, Polygon) is False:
                    self.initializeFailed("[%s] '%s' invalid initialize, HintPoint %s must be inside polygon %s" % (
                        self.getParent().getName(), self.getName(), HintPoint, Polygon))

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
