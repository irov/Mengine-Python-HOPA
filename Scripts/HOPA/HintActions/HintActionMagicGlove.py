from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionMagicGlove(MixinObject, HintActionDefault):

    def _onParams(self, params):
        super(HintActionMagicGlove, self)._onParams(params)
        self.rune_id = params["Rune_ID"]
        self.demon_object = DemonManager.getDemon('MagicGlove')

    def _getHintObject(self):
        return self.demon_object

    def _onCheck(self):
        if self.rune_id in self.demon_object.getParam("Runes"):
            return True
        return False

    def _getHintPosition(self, demon_object):
        entity_object = demon_object.getEntity()
        hotspot = entity_object.getCurrentStateButton()
        pos = hotspot.getCurrentMovieSocketCenter()
        return pos

