from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault


class SparksActionItemUseInventoryItem(SparksActionDefault, MixinItem):
    def __init__(self):
        super(SparksActionItemUseInventoryItem, self).__init__()

        self.InventoryItem = None
        pass

    def _onParams(self, params):
        super(SparksActionItemUseInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        return True
        pass

    def _getSparksObject(self):
        return self.Item
        pass

    def _getSparksPosition(self, item):
        itemEntity = item.getEntity()

        Sprite = itemEntity.getSprite()
        Position = Sprite.getWorldImageCenter()

        return Position
        pass

    def _changeEmmiterForm(self, effectObject):
        Entity = self.Item.getEntity()

        Hotspot = Entity.getHotSpot()

        if Hotspot.isCompile() is False:
            return False
            pass

        width = Hotspot.getWidth()
        height = Hotspot.getHeight()

        effectObject.setPosition((width * 0.5, height * 0.5))

        emitters = effectObject.getMovieNodies("ParticleEmitter2")

        for movie, emitter in emitters:
            emitter.setEmitterPositionRelative(True)
            emitter.setEmitterRandomMode(True)

            ResourceHIT = Hotspot.getResourceHIT()
            emitter.changeEmitterImage(ResourceHIT)
            pass

        return True
        pass

    pass
