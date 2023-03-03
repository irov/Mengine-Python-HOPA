from Foundation.Task.MixinObjectTemplate import MixinItem

from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionItem(HintActionDefault, MixinItem):

    def _getHintObject(self):
        return self.Item

    def _getHintPosition(self, Item):
        if Item.getType() == "ObjectMovieItem" or Item.getType() == "ObjectMovie2Item":
            entity = Item.getEntity()

            if entity is not None:
                return entity.getHintPoint()

        elif Item.hasParam("HintPoint"):
            return Item.calcWorldHintPoint()

        Trace.log("HintAction", 0, "HintActionItem ItemName %s ItemType %s cant calculate position" % (Item.getName(), Item.getType()))

        return 0.0, 0.0, 0.0
