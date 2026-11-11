from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObjectTemplate import MixinItem
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

    def _onAction(self, source):
        if self.hintObject is not None:
            print("CruiseActionItemWithItemPopup._onAction:type = %s, " % (self.getType()), self.hintObject.getName(),
            self.hintObject.getGroupName() or " [not cruise!! object]")
            pass
        else:
            print("CruiseActionItemWithItemPopup._onAction:type = %s, " % (self.getType()), " [not cruise!!!! object]")
            pass

        PositionToItem = self._getCruisePositionToItem(self.hintObject)
        PositionToButton = self._getCruisePositionToButton()

        def _filter(item_name):
            InventoryItem = ItemManager.getItemObject(item_name)

            if InventoryItem is self.hintObject:
                return True
            return False

        source.addTask("AliasCruiseControlAction", Position=PositionToItem, Object=self.hintObject)

        source.addListener(Notificator.onItemPopUpOpen, Filter=_filter)
        source.addTask("AliasCruiseControlAction", Position=PositionToButton)
        source.addListener(Notificator.onItemPopUpClose, Filter=_filter)

        source.addNotify(Notificator.onCruiseActionEnd, self)
        pass

    pass
