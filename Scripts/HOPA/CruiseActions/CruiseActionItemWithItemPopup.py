from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.TaskManager import TaskManager
from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault
from HOPA.ItemManager import ItemManager


class CruiseActionItemWithItemPopup(CruiseActionDefault, MixinItem):
    def _onParams(self, params):
        super(CruiseActionItemWithItemPopup, self)._onParams(params)
        pass

    def _getCruiseObject(self):
        return self.Item
        pass

    def _onCheck(self):
        return True
        pass

    def _getCruisePositionToItem(self, Item):
        cruisePoint = Item.calcWorldHintPoint()
        if cruisePoint is not None:
            return cruisePoint

        ItemEntity = Item.getEntity()

        hotspot = ItemEntity.getHotSpot()
        size = Mengine.getHotSpotImageSize(hotspot)
        world_position = hotspot.getWorldPosition()

        Position = (world_position.x + size.x / 2, world_position.y + size.y / 2)

        # - position by sprite center ----------------
        # Sprite = ItemEntity.getSprite()
        # Position = Sprite.getWorldImageCenter()
        # --------------------------------------------

        return Position
        pass

    def _getCruisePositionToButton(self):
        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        Object = Demon.getObject("Button_Ok")
        ObjectEntity = Object.getEntity()

        CruisePoint = Object.calcWorldHintPoint()
        if CruisePoint is not None:
            return CruisePoint
        hotspot = ObjectEntity.getHotSpot()
        Position = hotspot.getWorldPolygonCenter()

        return Position
        pass

    def _onAction(self):
        if self.hintObject is not None:
            print("CruiseActionItemWithItemPopup._onAction:type = %s, " % (self.getType()), self.hintObject.getName(),
            self.hintObject.getGroupName() or " [not cruise!! object]")
            pass
        else:
            print("CruiseActionItemWithItemPopup._onAction:type = %s, " % (self.getType()), " [not cruise!!!! object]")
            pass

        PositionToItem = self._getCruisePositionToItem(self.hintObject)
        PositionToButton = self._getCruisePositionToButton()

        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")
            pass

        def _filter(item_name):
            InventoryItem = ItemManager.getItemObject(item_name)

            if InventoryItem is self.hintObject:
                return True
            return False

        with TaskManager.createTaskChain(Name="CruiseActionDefault") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionToItem, Object=self.hintObject)

            tc.addTask("TaskListener", ID=Notificator.onItemPopUpOpen, Filter=_filter)
            tc.addTask("AliasCruiseControlAction", Position=PositionToButton)
            tc.addTask("TaskListener", ID=Notificator.onItemPopUpClose, Filter=_filter)

            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass

    pass
