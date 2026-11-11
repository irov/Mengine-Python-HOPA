from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.CruiseAction import CruiseAction
from HOPA.ItemManager import ItemManager


class CruiseActionGiveItemOr(MixinObject, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionGiveItemOr, self)._onParams(params)

        self.ItemNames = params["ItemNames"]
        self.InventoryItem = None
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        for name in self.ItemNames[:]:
            InventoryItem = ItemManager.getItemInventoryItem(name)
            if self.Inventory.hasInventoryItem(InventoryItem) is True:
                self.InventoryItem = InventoryItem
                return True

        return False

    def _onAction(self, source):
        PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
        source.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)
        source.addScope(self.showCruise)
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
            pass

        else:
            cruisePoint = self.Object.calcWorldHintPoint()
            if cruisePoint is not None:
                PositionTo2 = cruisePoint
                pass
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()
                pass

        source.addTask("AliasCruiseControlAction", Position=PositionTo1, Object=self.InventoryItem)
        source.addTask("AliasCruiseControlAction", Position=PositionTo2, Object=self.Object)
        source.addNotify(Notificator.onCruiseActionEnd, self)
