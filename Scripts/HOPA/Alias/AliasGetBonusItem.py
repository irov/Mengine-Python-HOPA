from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.BonusItemManager import BonusItemManager


class AliasGetBonusItem(TaskAlias):
    def _onParams(self, params):
        super(AliasGetBonusItem, self)._onParams(params)
        self.BonusItemName = params.get("BonusItemName")

    def _onGenerate(self, source):
        BonusStoreObject = BonusItemManager.getItemStoreObject(self.BonusItemName)
        Point = BonusStoreObject.getPoint()

        BonusPartObject = BonusItemManager.getItemPartObject(self.BonusItemName)
        StartPosition = BonusItemManager.getItemPartStartPosition(self.BonusItemName)
        PositionTo = BonusPartObject.getPosition()

        P1 = (PositionTo[0], StartPosition.y)

        source.addTask("TaskEnable", Object=BonusPartObject, Value=True)
        source.addTask("TaskObjectSetPosition", Object=BonusPartObject, Value=StartPosition)

        time = 0.3
        time *= 1000  # speed fix

        with source.addParallelTask(2) as (source_0, source_1):
            source_0.addTask("AliasObjectAlphaTo", Object=BonusPartObject, From=0.0, To=1.0, Time=time)
            source_1.addTask("AliasObjectScaleTo", Object=BonusPartObject, From=(0.0, 0.0, 1.0), To=(1.2, 1.2, 1.0), Time=time)
            pass

        BonusItemMoveSpeed = DefaultManager.getDefaultFloat("BonusItemMoveSpeed", 600)
        BonusItemMoveSpeed *= 0.001  # speed fix
        time = 0.2
        time *= 1000  # speed fix
        source.addTask("TaskNodeBezier2To", Node=BonusPartObject.getEntity(), Point1=P1, To=PositionTo, Speed=BonusItemMoveSpeed)
        source.addTask("TaskObjectSetPosition", Object=BonusPartObject, Value=PositionTo)
        source.addTask("AliasObjectScaleTo", Object=BonusPartObject, To=(1.0, 1.0, 1.0), Time=time)

        #        BonusSceneObject = BonusItemManager.getItemSceneObject(self.BonusItemName)
        source.addTask("TaskFoundBonusItem", Item=BonusPartObject, BonusItemName=self.BonusItemName)
