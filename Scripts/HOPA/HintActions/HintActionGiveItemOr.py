from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.ItemManager import ItemManager


class HintActionGiveItemOr(MixinObject, HintActionMultiTarget):
    def _onParams(self, params):
        super(HintActionGiveItemOr, self)._onParams(params)

        self.ItemNames = params["ItemNames"]
        self.InventoryItem = None
        pass

    def _getHintObject(self):
        return self.Object
        pass

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        for name in self.ItemNames[:]:
            InventoryItem = ItemManager.getItemInventoryItem(name)
            if self.Inventory.hasInventoryItem(InventoryItem) is True:
                self.InventoryItem = InventoryItem
                return True
                pass
            pass

        return False
        pass

    def _onAction(self, hint):
        # print "HintActionGiveItemOr _onAction", self.InventoryItem
        # with TaskManager.createTaskChain(Name = "HintActionUseInventoryItem_Scrolling") as tc:
        #     PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
        #     tc.addTask(PolicyInventoryScrolling, InventoryItem = self.InventoryItem)
        #     tc.addTask("TaskFunction", Fn = self.showHint)
        #     pass
        # pass

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
            hintPoint = self.Object.calcWorldHintPoint()
            if hintPoint is not None:
                PositionTo2 = hintPoint
                pass
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()
                pass
            pass
        self.showHint(PositionTo1, PositionTo2)
