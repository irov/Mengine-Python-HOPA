from Foundation.Task.MixinObjectTemplate import MixinInteraction
from HOPA.QuestIconActions.QuestIconActionDefault import QuestIconActionDefault


class QuestIconActionInteraction(MixinInteraction, QuestIconActionDefault):
    def _onParams(self, params):
        super(QuestIconActionInteraction, self)._onParams(params)
        pass

    def _getQuestIconObject(self):
        return self.Interaction
        pass

    def _getQuestIconPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    pass
