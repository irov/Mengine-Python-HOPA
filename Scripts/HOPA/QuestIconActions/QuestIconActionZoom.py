from Foundation.Task.MixinObjectTemplate import MixinZoom
from HOPA.QuestIconActions.QuestIconActionDefault import QuestIconActionDefault


class QuestIconActionZoom(MixinZoom, QuestIconActionDefault):
    def _onParams(self, params):
        super(QuestIconActionZoom, self)._onParams(params)
        pass

    def _getQuestIconObject(self):
        return self.Zoom
        pass

    def _getQuestIconPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    pass
