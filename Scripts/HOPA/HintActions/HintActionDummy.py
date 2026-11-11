from Foundation.Task.MixinGroup import MixinGroup
from HOPA.HintAction import HintAction


class HintActionDummy(MixinGroup, HintAction):
    def _onAction(self, source, hint):
        self.setEnd()
        pass

    pass
