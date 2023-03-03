from Foundation.Task.MixinObjectTemplate import MixinTransition
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault


class SparksActionTransition(SparksActionDefault, MixinTransition):
    def _onParams(self, params):
        super(SparksActionTransition, self)._onParams(params)
        pass

    def _getSparksObject(self):
        return self.Transition
        pass

    def _getSparksPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    def _onCheck(self):
        if self.Transition is None:
            return False
        Enable = self.Transition.getParam("Enable")
        if Enable is False:
            return False

        Open = self.Transition.getParam("Enable")
        if Open is False:
            return False

        BlockOpen = self.Transition.getParam("BlockOpen")
        if BlockOpen is True:
            return False

        return True
        pass

    def _changeEmmiterForm(self, effectObject):
        polygon = self.Transition.getPolygon()

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
