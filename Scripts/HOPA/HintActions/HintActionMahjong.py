import Trace

from Foundation.Task.MixinObject import MixinObject

from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget

class HintActionMahjong(MixinObject, HintActionMultiTarget):

    def _onParams(self, params):
        super(HintActionMahjong, self)._onParams(params)

        self.Object2 = params["Object2"]

    def _getHintObject(self):
        return self.Object

    def _onAction(self, hint):
        points = self.getHintDoublePosition(hint)
        self.showHint(*points)

    def _getHintDoublePosition(self, hint):
        if self.Object is not None and self.Object2 is not None:
            if self.Object.getType() == "ObjectMovie2Button" and self.Object2.getType() == "ObjectMovie2Button":
                if self.Object.isActive() and self.Object2.isActive():
                    Pos = self.Object.entity.getCurrentMovieSocketCenter()
                    Pos2 = self.Object2.entity.getCurrentMovieSocketCenter()

                    if Pos is not None and Pos2 is not None:
                        return Pos, Pos2

            elif self.Object.hasParam("HintPoint") and self.Object2.hasParam("HintPoint"):  # for ObjectButton

                Pos = self.Object.calcWorldHintPoint()
                Pos2 = self.Object2.calcWorldHintPoint()

                if Pos is not None and Pos2 is not None:
                    return Pos, Pos2

        Trace.log("HintAction", 0, "HintActionMahjong ItemName %s ItemType %s or ItemName %s ItemType %s"
                                   " cant calculate position" % (self.Object.name, self.Object.getType(), self.Object2.name, self.Object2.getType()))

        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)