from HOPA.HintAction import HintAction


class HintActionFindHiddenItem(HintAction):  # , MixinObject):
    def _onParams(self, params):
        super(HintActionFindHiddenItem, self)._onParams(params)
        pass

    def _onCheck(self):
        return True
        pass

    def _onAction(self, source, hint):
        source.addTask("AliasMindPlay", MindID="ID_MIND_FIND_HIDDEN_ITEM")

    pass
