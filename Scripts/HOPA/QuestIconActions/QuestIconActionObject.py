from Foundation.Task.MixinObject import MixinObject
from HOPA.QuestIconActions.QuestIconActionDefault import QuestIconActionDefault

class QuestIconActionObject(MixinObject, QuestIconActionDefault):
    def _onParams(self, params):
        super(QuestIconActionObject, self)._onParams(params)
        pass

    def _getQuestIconObject(self):
        return self.Object
        pass

    def _getQuestIconPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass
    pass