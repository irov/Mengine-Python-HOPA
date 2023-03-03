from Foundation.Object.DemonObject import DemonObject


class ObjectCollectedAmulet(DemonObject):
    def _onParams(self, params):
        super(ObjectCollectedAmulet, self)._onParams(params)
        self.initParam("Size", params, 5)
        self.initParam("CurrentCount", params, 0)
        self.initParam("CurrentState", params, "Locked")
        self.initParam("HintPoint", params, None)
        pass

    def calcWorldHintPoint(self):
        hintPoint = self.getHintPoint()

        if hintPoint is None:
            return None
            pass

        groupScene = self.getGroup()

        slot = groupScene.getScene()

        posScene = slot.getLocalPosition()

        pos = (posScene.x + hintPoint[0], posScene.y + hintPoint[1])

        return pos
