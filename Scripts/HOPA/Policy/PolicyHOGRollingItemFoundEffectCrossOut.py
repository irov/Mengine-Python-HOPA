from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager

class PolicyHOGRollingItemFoundEffectCrossOut(TaskAlias):
    def _onParams(self, params):
        super(PolicyHOGRollingItemFoundEffectCrossOut, self)._onParams(params)
        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        InventoryEntity = HOGInventory.getEntity()
        slot = InventoryEntity.getSlotByName(self.HOGItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        P2 = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()

        Item = self.Group.getObject(self.ItemName)
        Item.setBlock(False)
        ItemEntity = Item.getEntity()
        pure = ItemEntity.generatePure()
        pure.enable()

        tempPos = ItemEntity.getCameraPosition(Camera)
        offset = pure.getWorldPosition()
        offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)
        pureCenter = pure.getLocalImageCenter()

        P0 = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)

        P1 = (P2.x, P0[1])

        layerGroup = GroupManager.getGroup("HOGViewport")

        mainLayer = layerGroup.getMainLayer()
        mainLayer.addChild(pure)

        pure.setLocalPosition(P0)
        pure.setOrigin(pureCenter)

        length = Mengine.length_v2_v2(P1, P2)

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGItemIncreaseTime", 1)
        HOGItemIncreaseTime *= 1000  # speed fix

        time = length / HOGItemHideEffectSpeed
        # time *= 1000  # speed fix

        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.5, 1.5, 1.0), Time=HOGItemIncreaseTime)

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=pure, Point1=P1, To=P2, Speed=HOGItemHideEffectSpeed)

            tcp1.addTask("TaskNodeScaleTo", Node=pure, To=(0.4, 0.4, 1.0), Time=time)
            pass

        source.addTask("TaskNodeRemoveFromParent", Node=pure)
        source.addTask("TaskNodeDestroy", Node=pure)
        source.addTask("TaskHOGRollingInventoryCrossOut", HOGItemName=self.HOGItemName)
        pass

    pass