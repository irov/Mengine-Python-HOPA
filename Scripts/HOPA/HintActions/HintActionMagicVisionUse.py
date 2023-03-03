from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionMagicVisionUse(HintActionDefault):
    def _onParams(self, params):
        super(HintActionMagicVisionUse, self)._onParams(params)
        pass

    def _onInitialize(self):
        self.CheckSceneName = self.Quest.params.get("SceneNameTo")
        self.MVDemon = self.Quest.params.get("Demon")
        self.hintObject = self._getHintObject()
        pass

    def _getHintObject(self):
        DemonEntity = self.MVDemon.getEntity()
        clickObject = DemonEntity.getSocket()
        return clickObject
        pass

    def _getHintPosition(self, clickObject):
        clickObjectEntity = clickObject.getEntity()
        if clickObject.hasParam("HintPoint") is True:
            hintPoint = clickObject.calcWorldHintPoint()
            if hintPoint is not None:
                return hintPoint
                pass
            pass

        hotspot = clickObjectEntity.getHotSpot()
        Position = hotspot.getWorldPolygonCenter()
        return Position
        pass

    def _onCheck(self):
        Enable = self.MVDemon.getEnable()
        if Enable is False:
            return False
            pass

        blocks = self.MVDemon.getBlockedScenes()
        dones = self.MVDemon.getCompletedScenes()

        if self.CheckSceneName in blocks:
            return False
            pass

        elif self.CheckSceneName in dones:
            return False
            pass
        return True
        pass

    pass
