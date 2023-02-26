from Foundation.Task.MixinObjectTemplate import MixinItem

from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault

class CruiseActionItem(CruiseActionDefault, MixinItem):

    def _getCruiseObject(self):
        return self.Item

    def _getCruisePosition(self, Item):
        if Item.getType() == "ObjectMovieItem" or Item.getType() == "ObjectMovie2Item":
            entity = Item.getEntity()

            if entity is not None:
                return entity.getHintPoint()

        elif Item.getType() is "ObjectItem":
            return Item.calcWorldHintPoint()

        Trace.log("CruiseAction", 0, "CruiseActionItem ItemName %s ItemType %s cant calculate position" % (Item.getName(), Item.getType()))

        return 0.0, 0.0, 0.0