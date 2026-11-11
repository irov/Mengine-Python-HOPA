from HOPA.CruiseAction import CruiseAction


class CruiseActionSpellUse(CruiseAction):
    def __init__(self):
        super(CruiseActionSpellUse, self).__init__()

    def _onParams(self, params):
        super(CruiseActionSpellUse, self)._onParams(params)
        self.Spell = params.get("Spell")
        self.Object = params.get("Object")

    def _getCruiseObject(self):
        return self.Spell

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()
        Socket = ObjectEntity.getSocket()
        SocketEntity = Socket.getEntity()
        hotspot = SocketEntity.getHotSpot()
        Position = hotspot.getWorldPolygonCenter()
        return Position

    def _onCheck(self):
        State = self.Spell.getParam("CurrentState")
        if State != "Ready":
            return False
        return True

    def _onAction(self, source):
        self.showCruise(source)

    def showCruise(self, source):
        hObject = self._getCruiseObject()
        PositionTo1 = self._getCruisePosition(hObject)

        PlaceObjectType = self.Object.getType()

        if PlaceObjectType == "ObjectItem":
            ItemEntity = self.Object.getEntity()
            Sprite = ItemEntity.getSprite()

            PositionTo2 = Sprite.getWorldImageCenter()

        else:
            cruisePoint = self.Object.calcWorldHintPoint()
            if cruisePoint is not None:
                PositionTo2 = cruisePoint
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()

        source.addTask("AliasCruiseControlAction", Position=PositionTo1)
        source.addDelay(0.5 * 1000)  # speed fix
        source.addTask("AliasCruiseControlAction", Position=PositionTo2)
        source.addDelay(0.5 * 1000)  # speed fix
        source.addNotify(Notificator.onCruiseActionEnd, self)
