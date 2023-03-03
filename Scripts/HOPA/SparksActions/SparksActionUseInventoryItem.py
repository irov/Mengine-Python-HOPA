from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault


class SparksActionUseInventoryItem(SparksActionDefault, MixinObject):
    def __init__(self):
        super(SparksActionUseInventoryItem, self).__init__()
        pass

    def _onParams(self, params):
        super(SparksActionUseInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        if self.Object.active is False:
            return False
            pass

        return True
        pass

    def _getSparksObject(self):
        return self.Object
        pass

    def _getSparksPosition(self, Object):
        ObjectEntity = Object.getEntity()

        hotspot = ObjectEntity.getHotSpot()
        Position = hotspot.getWorldPolygonCenter()

        return Position
        pass

    def _changeEmmiterForm(self, effectObject):
        polygon = self.Object.getPolygon()

        effectObject.setPosition((0, 0))

        emitters = effectObject.getMovieNodies("ParticleEmitter2")

        for movie, emitter in emitters:
            emitter.setEmitterPositionRelative(True)
            emitter.setEmitterRandomMode(True)
            # emitter.setEmitterPolygon(polygon)
            emitter.changeEmitterPolygon(polygon)
            pass

        return True
        pass

    pass
