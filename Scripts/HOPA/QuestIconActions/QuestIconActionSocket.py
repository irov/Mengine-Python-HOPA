from Foundation.Task.MixinObjectTemplate import MixinSocket
from HOPA.QuestIconActions.QuestIconActionDefault import QuestIconActionDefault

class QuestIconActionSocket(MixinSocket, QuestIconActionDefault):
    def _onParams(self, params):
        super(QuestIconActionSocket, self)._onParams(params)
        pass

    def _getQuestIconObject(self):
        return self.Socket
        pass

    def _getQuestIconPosition(self, Object):
        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
        pass

    pass