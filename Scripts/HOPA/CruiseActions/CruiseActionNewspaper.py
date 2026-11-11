from Foundation.Task.MixinObject import MixinObject
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionNewspaper(CruiseAction, MixinObject):
    def _onParams(self, params):
        super(CruiseActionNewspaper, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionNewspaper')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionNewspaper')

    def _getCruiseObject(self):
        return self.Object

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
        else:
            CruisePoint = Object.calcWorldHintPoint()
            if CruisePoint is not None:
                return CruisePoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()

        return Position

    def _onCheck(self):
        return True

    def _onAction(self, source):
        PositionTo = self._getCruisePosition(self.Object)

        source.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
        source.addDelay(self.click_delay)
        source.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
        source.addDelay(self.move_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
