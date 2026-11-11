from Foundation.Task.MixinObject import MixinObject
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionUseHOGFittingItem(MixinObject, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionUseHOGFittingItem, self)._onParams(params)
        self.InventoryItem = params["InventoryItem"]
        self.Inventory = params["Inventory"]
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionUseHOGFittingItem')

    def _onCheck(self):
        if self.Inventory is None:
            return False
        HogInventoryEnt = self.Inventory.getEntity()

        if HogInventoryEnt.ItemInSlot(self.InventoryItem) is False:
            return False
        return True

    def _onAction(self, source):
        self.showCruise(source)
        pass

    def showCruise(self, source):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo1 = Sprite.getWorldImageCenter()

        PlaceObjectType = self.Object.getType()

        if PlaceObjectType == "ObjectItem":
            ItemEntity = self.Object.getEntity()
            Sprite = ItemEntity.getSprite()

            PositionTo2 = Sprite.getWorldImageCenter()

        else:
            cruisePoint = self.Object.calcWorldHintPoint()
            if cruisePoint is not None:
                PositionTo2 = cruisePoint
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()

        source.addTask("AliasCruiseControlAction", Position=PositionTo1, Object=self.InventoryItem)
        source.addTask("AliasCruiseControlAction", Position=PositionTo2, Object=self.Object)
        source.addDelay(self.click_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
