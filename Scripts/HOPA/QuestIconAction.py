from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.Task.MixinScene import MixinScene

class QuestIconAction(MixinScene, Params, Initializer):
    def __init__(self):
        super(QuestIconAction, self).__init__()
        self.parentQuestIconObject = None
        pass

    def _onParams(self, params):
        super(QuestIconAction, self)._onParams(params)
        pass

    def setQuest(self, quest):
        self.Quest = quest
        pass

    def setParentQuestIconObject(self, questIconObj):
        self.parentQuestIconObject = questIconObj
        pass

    def getParentQuestIconObject(self):
        return self.parentQuestIconObject
        pass

    def onAction(self):
        self._onAction()
        pass

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        pass

    def _onAction(self):
        pass

    pass