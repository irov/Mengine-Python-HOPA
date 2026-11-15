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

    def __scopeClickOk(self, source):
        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        if Demon.hasObject("Movie2Button_Ok") is True:
            button = Demon.getObject("Movie2Button_Ok")
        else:
            button = Demon.getObject("Button_Ok")

        source.addTask("AliasCruiseControlAction", Object=button)

    def _onAction(self, source):
        PositionToItem = self._getCruisePositionToItem(self.hintObject)

        def _filter(item_name):
            InventoryItem = ItemManager.getItemObject(item_name)
            if InventoryItem is not self.hintObject:
                return False

            return True

        with source.addParallelTask(2) as (tc_open, tc_click):
            tc_open.addListener(Notificator.onItemPopUpOpen, Filter=_filter)
            tc_click.addTask("AliasCruiseControlAction", Position=PositionToItem, Object=self.hintObject)

        with source.addParallelTask(2) as (tc_close, tc_click):
            tc_close.addListener(Notificator.onItemPopUpClose, Filter=_filter)
            tc_click.addScope(self.__scopeClickOk)

        source.addNotify(Notificator.onCruiseActionEnd, self)
