from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget


class HintActionUseInventoryItem(MixinObject, HintActionMultiTarget):
    def _onParams(self, params):
        super(HintActionUseInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]

    def _getHintObject(self):
        return self.Object

    def _onCheck(self):
        self.Inventory = DemonManager.getDemon("Inventory")

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
        if self.InventoryItem.checkCount() is False:
            return False

        return True

    def getFollow_Node(self):
        return self.InventoryItem.getEntityNode()

    def _onActionStart(self, hint):
        self._runScrolling(hint)

    def _onScroll(self, source):
        PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling", "PolicyInventoryScrollingDefault")
        source.addNotify(Notificator.onInventoryRise)
        source.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)

    def getMultiHintPosition(self):
        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()
        PositionTo1 = Sprite.getWorldImageCenter()

        if self.Object.hasParam("HintPoint") is True:
            PositionTo2 = self.Object.calcWorldHintPoint()

            if PositionTo2 is not None:
                return PositionTo1, PositionTo2

        ObjectEntity = self.Object.getEntity()
        Sprite = ObjectEntity.getSprite()
        PositionTo2 = Sprite.getWorldImageCenter()

        return PositionTo1, PositionTo2

    def _onAction(self, source, hint):
        Offset = (50.0, 50.0)
        PositionTo1, PositionTo2 = self.getMultiHintPosition()

        self.showHint(source, PositionTo1, PositionTo2, Offset)

    def getHintLayer(self):
        scene = SceneManager.getCurrentScene()
        layer = scene.getSlot("HintEffect")
        return layer
