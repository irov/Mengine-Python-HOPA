from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget


class HintActionUseHOGFittingItem(MixinObject, HintActionMultiTarget):
    def _onParams(self, params):
        super(HintActionUseHOGFittingItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        self.Inventory = params["Inventory"]

    def _onCheck(self):
        if self.Inventory is None:
            return False

        if self.Inventory.isActive() is False:
            return False

        HogInventoryEnt = self.Inventory.getEntity()
        if HogInventoryEnt.ItemInSlot(self.InventoryItem) is False:
            return False

        return True

    def _getHintObject(self):
        return self.Object

    def _getHintDoublePosition(self, _hint):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        PositionTo1 = Sprite.getWorldImageCenter()

        ObjectEntity = self.Object.getEntity()

        if self.Object.hasParam("HintPoint") is True:
            hintPoint = self.Object.calcWorldHintPoint()

            if hintPoint is not None:
                PositionTo2 = hintPoint

            else:
                HotSpot = ObjectEntity.getHotSpot()
                PositionTo2 = HotSpot.getWorldPolygonCenter()

        else:
            Sprite = ObjectEntity.getSprite()
            PositionTo2 = Sprite.getWorldImageCenter()

        return PositionTo1, PositionTo2

    def _onAction(self, hint):
        hint_points = self.getHintDoublePosition(hint)
        self.showHint(*hint_points)

    def getHintLayer(self):
        scene = SceneManager.getCurrentScene()
        layer = scene.getSlot("HintEffect")
        return layer
