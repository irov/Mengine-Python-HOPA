from HOPA.HintActions.HintActionDefault import HintActionDefault

class HintActionEnvSpellUse(HintActionDefault):
    def _onParams(self, params):
        super(HintActionEnvSpellUse, self)._onParams(params)
        self.Spell = params.get("Spell")
        pass

    def _getHintObject(self):
        return self.Spell
        pass

    def _getHintPosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
            pass
        else:
            if Object.hasParam("HintPoint") is True:
                hintPoint = Object.calcWorldHintPoint()
                if hintPoint is not None:
                    return hintPoint
                    pass
                pass
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()
            pass

        return Position
        pass

    def _onCheck(self):
        State = self.Spell.getParam("CurrentState")
        if State != "Ready":
            return False
            pass

        return True
        pass

    pass