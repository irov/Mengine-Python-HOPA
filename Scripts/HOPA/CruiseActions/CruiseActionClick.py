from Foundation.Task.MixinObject import MixinObject

from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault


class CruiseActionClick(CruiseActionDefault, MixinObject):
    def _getCruiseObject(self):
        return self.Object

    def _getCruisePosition(self, Object):
        if Object.getType() == "ObjectMovieItem" or Object.getType() == "ObjectMovie2Item":
            entity = Object.getEntity()

            if entity is not None:
                return entity.getHintPoint()

        elif Object.hasParam("HintPoint"):
            return Object.calcWorldHintPoint()

        elif Object.getType() == "ObjectMovie2":
            pos = Object.getFirstSocketTuple()[2].getWorldPolygonCenter()

            if pos is not None:
                return pos

        Trace.log("CruiseAction", 0, "CruiseActionClick ItemName %s ItemType %s cant calculate position" % (Object.getName(), Object.getType()))

        return 0.0, 0.0, 0.0
