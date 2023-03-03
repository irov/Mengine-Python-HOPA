from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager

from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionHOGItem(HintActionDefault):

    def _onParams(self, params):
        super(HintActionHOGItem, self)._onParams(params)

        self.ItemName = params["ItemName"]
        self.HogGroupName = params["HogGroupName"]
        self.IgnoreShadow = params.get("IgnoreShadow", True)
        self.HogItem = params.get("HogItem", None)

    def _onCheck(self):
        if self.HogItem is None:
            return True

        if self.HogItem.getActivate() is False:
            return False

        return True

    def _getHintObject(self):
        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            DemonHOG = GroupManager.getObject(self.GroupName, self.HogGroupName)
            HogItem = DemonHOG.getObject(self.ItemName)
            return HogItem

        HogItem = GroupManager.getObject(self.GroupName, self.ItemName)

        return HogItem

    def _getHintPosition(self, Item):
        if Item.getType() == "ObjectMovie2Item" or Item.getType() == "ObjectMovieItem":
            return Item.entity.getHintPoint()

        hintPoint = Item.calcWorldHintPoint()

        if hintPoint is not None:
            return hintPoint

        ItemEntity = Item.getEntity()

        if self.IgnoreShadow:
            Sprite = ItemEntity.generatePure()
            pureCenter = Sprite.getLocalImageCenter()
            Camera = Mengine.getRenderCamera2D()
            tempPos = ItemEntity.getCameraPosition(Camera)
            offset = Sprite.getWorldPosition()
            offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)
            Position = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)

        else:
            Sprite = ItemEntity.getSprite()
            Position = Sprite.getWorldImageCenter()

        return Position
