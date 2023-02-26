from Foundation.Task.MixinObject import MixinObject
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault

class SparksActionClick(SparksActionDefault, MixinObject):
    def _onParams(self, params):
        super(SparksActionClick, self)._onParams(params)
        pass

    def _getSparksObject(self):
        return self.Object
        pass

    def _getSparksPosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getParam("Type") == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
            pass
        else:
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()
            pass

        return Position
        pass

    def _onCheck(self):
        BlockInteractive = self.Object.getParam("BlockInteractive")
        if BlockInteractive is True:
            return False
            pass
        if self.Object.active is False:
            return False
            pass

        return True
        pass

    def _changeEmmiterForm(self, effectObject):
        if self.Object.getType() == "ObjectItem":
            Entity = self.Object.getEntity()

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
                ResourceHITName = ResourceHIT.getName()
                emitter.changeEmitterImage(ResourceHITName)
                pass
            pass
        else:
            polygon = self.Object.getPolygon()

            effectObject.setPosition((0, 0))

            emitters = effectObject.getMovieNodies("ParticleEmitter2")

            for movie, emitter in emitters:
                dirs = dir(emitter)
                # print
                # for attr in dirs:
                #     print attr
                #     pass
                # print
                emitter.setEmitterPositionRelative(True)
                emitter.setEmitterRandomMode(True)
                # emitter.setEmitterPolygon(polygon)
                emitter.changeEmitterPolygon(polygon)
                pass
            pass

        return True
        pass

    pass