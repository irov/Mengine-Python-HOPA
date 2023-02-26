from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasHOGFittingMoveItemToSlot(TaskAlias):
    def __init__(self):
        super(AliasHOGFittingMoveItemToSlot, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasHOGFittingMoveItemToSlot, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.ItemObject = params.get("ItemObject")
        self.InventoryItemObject = params.get("InventoryItemObject")
        pass

    def _onInitialize(self):
        super(AliasHOGFittingMoveItemToSlot, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        # if ArrowManager.emptyArrowAttach() is False :
        #     Notification.notify(Notificator.onHOGFittinItemReturn)
        #     pass

        InventoryEntity = self.Inventory.getEntity()

        slot = InventoryEntity.getSlotByName(self.ItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.ItemName))
            pass

        P2 = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()

        ItemEntity = self.ItemObject.getEntity()
        pure = ItemEntity.generatePure()
        pure.enable()

        tempPos = ItemEntity.getCameraPosition(Camera)
        offset = pure.getWorldPosition()
        offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)
        pureCenter = pure.getLocalImageCenter()

        P0 = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)

        P1 = (P2.x, P0[1])

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("HOGViewport")
        layer_InventoryItemEffect.addChild(pure)

        pure.setLocalPosition(P0)
        pure.setOrigin(pureCenter)

        length = Mengine.length_v2_v2(P1, P2)

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGFittingItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGFittingItemIncreaseTime", 0.3)
        HOGItemIncreaseTime *= 1000  # speed fix

        time = length / HOGItemHideEffectSpeed
        if time < 15:
            time = 15.0

        # time *= 1000  # speed fix

        # source.addNotify(Notificator.onInventoryPickInventoryItem, slot.ItemHideStore)

        source.addNotify(Notificator.onInventorySlotItemLeave, self.Inventory, slot.ItemHideStore)

        source.addFunction(slot.DisableSocket)

        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.5, 1.5, 1.0), Time=HOGItemIncreaseTime)

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=pure, Point1=P1, To=P2, Speed=HOGItemHideEffectSpeed)

            tcp1.addTask("TaskNodeScaleTo", Node=pure, To=(0.4, 0.4, 1.0), Time=time)
            pass

        source.addTask("TaskNodeRemoveFromParent", Node=pure)
        source.addTask("TaskNodeDestroy", Node=pure)

        source.addFunction(slot.EnableSocket)
        pass
    pass