from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasFanBezier2To(TaskAlias):
    def _onParams(self, params):
        super(AliasFanBezier2To, self)._onParams(params)
        self.FanItemGroupName = params.get("FanItemGroupName")
        self.FanItemName = params.get("FanItemName")
        pass

    def _onGenerate(self, source):
        FromXY = Mengine.getCursorPosition()
        objItem = GroupManager.getObject(self.FanItemGroupName, self.FanItemName)
        objItemSprite = objItem.getObject("Sprite_Item")
        FanEntity = objItemSprite.getEntity()
        FanItemPosition = FanEntity.getWorldPosition()

        Image = FanEntity.getSprite()
        ImageSize = Image.getSurfaceSize()

        P1 = (FromXY.x, FromXY.y)
        P2 = (FanItemPosition.x + ImageSize.x * 0.5, FanItemPosition.y + ImageSize.y * 0.5)
        p1x = P1[0] if P1[1] > P2[1] else P2[0]
        p1y = P2[1] if P1[1] > P2[1] else P1[1]

        # P1 = (p1x, p1y)

        source.addTask("AliasObjectBezier2To", GroupName=self.FanItemGroupName, ObjectName=self.FanItemName,
                       Point1=P1, To=P2, Speed=600 * 0.001)  # speed fix
