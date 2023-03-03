from Foundation.Task.MixinObjectTemplate import MixinItem
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault


class SparksActionItem(SparksActionDefault, MixinItem):

    def _onCheck(self):
        return self.Item.isActive()

    def _getSparksObject(self):
        return self.Item

    def _getSparksPosition(self, Item):
        if Item.getType() is "ObjectMovieItem" or Item.getType() is "ObjectMovie2Item":
            entity = Item.getEntity()

            if entity is not None:
                return entity.getHintPoint()

        elif Item.hasParam("HintPoint"):
            return Item.calcWorldHintPoint()

        else:
            Trace.log("SparksAction", 0, "SparksAction ItemName %s ItemType %s cant calculate position" % (Item.getName(), Item.getType()))

            return 0.0, 0.0, 0.0

    def _changeEmmiterForm(self, effectObject):
        effectObject.setPosition(self._getSparksPosition(self.Item))

        emitters = effectObject.getMovieNodies("ParticleEmitter2")

        for movie, emitter in emitters:
            emitter.setEmitterPositionRelative(True)
            emitter.setEmitterRandomMode(True)

        return True
