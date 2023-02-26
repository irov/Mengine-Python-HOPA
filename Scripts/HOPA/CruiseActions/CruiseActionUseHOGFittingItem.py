from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionUseHOGFittingItem(MixinObject, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionUseHOGFittingItem, self)._onParams(params)
        self.InventoryItem = params["InventoryItem"]
        self.Inventory = params["Inventory"]
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionUseHOGFittingItem')
        pass

    def _onCheck(self):
        if self.Inventory is None:
            return False
            pass
        HogInventoryEnt = self.Inventory.getEntity()

        if HogInventoryEnt.ItemInSlot(self.InventoryItem) is False:
            return False
            pass
        return True
        pass

    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionUseHOGFittingItem_Cruise") is True:
            TaskManager.cancelTaskChain("CruiseActionUseHOGFittingItem_Cruise")
            pass
        self.showCruise()
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

        with TaskManager.createTaskChain(Name="CruiseActionUseHOGFittingItem_Cruise") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo1, Object=self.InventoryItem)
            tc.addTask("AliasCruiseControlAction", Position=PositionTo2, Object=self.Object)
            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass

    def _onEnd(self):
        super(CruiseActionUseHOGFittingItem, self)._onEnd()

        pass
    pass