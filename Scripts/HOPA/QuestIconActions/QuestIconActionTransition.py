from Foundation.Task.MixinObjectTemplate import MixinTransition
from HOPA.QuestIconActions.QuestIconActionDefault import QuestIconActionDefault


class QuestIconActionTransition(MixinTransition, QuestIconActionDefault):
    def _onParams(self, params):
        super(QuestIconActionTransition, self)._onParams(params)
        pass

    def _getQuestIconObject(self):
        return self.Transition
        pass

    def _getQuestIconPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    pass
