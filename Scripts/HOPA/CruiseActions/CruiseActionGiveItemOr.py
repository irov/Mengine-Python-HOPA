from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
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

    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionUseInventoryItem_Scrolling") is True:
            TaskManager.cancelTaskChain("CruiseActionUseInventoryItem_Scrolling")
            pass

        if TaskManager.existTaskChain("CruiseActionUseInventoryItem_Cruise") is True:
            TaskManager.cancelTaskChain("CruiseActionUseInventoryItem_Cruise")
            pass

        with TaskManager.createTaskChain(Name="CruiseActionUseInventoryItem_Scrolling") as tc:
            PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
            tc.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)
            tc.addTask("TaskFunction", Fn=self.showCruise)
            pass
        pass

    def showCruise(self):
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
            pass

        with TaskManager.createTaskChain(Name="CruiseActionUseInventoryItem_Cruise") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo1, Object=self.InventoryItem)
            tc.addTask("AliasCruiseControlAction", Position=PositionTo2, Object=self.Object)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def _onEnd(self):
        super(CruiseActionGiveItemOr, self)._onEnd()
