from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager

from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault


class CruiseActionHOGItem(CruiseActionDefault):
    def _onParams(self, params):
        super(CruiseActionHOGItem, self)._onParams(params)

        self.ItemName = params["ItemName"]
        self.HogGroupName = params["HogGroupName"]
        self.IgnoreShadow = params.get("IgnoreShadow", True)

    def _getCruiseObject(self):
        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            DemonHOG = GroupManager.getObject(self.GroupName, self.HogGroupName)
            HogItem = DemonHOG.getObject(self.ItemName)
            return HogItem

        HogItem = GroupManager.getObject(self.GroupName, self.ItemName)

        return HogItem

    def _getCruisePosition(self, Item):
        if Item.getType() == "ObjectMovieItem" or Item.getType() == "ObjectMovie2Item":
            entity = Item.getEntity()

            if entity is not None:
                return entity.getHintPoint()

        elif Item.hasParam("HintPoint"):
            return Item.calcWorldHintPoint()

        Trace.log("CruiseAction", 0, "CruiseActionHOGItem ItemName %s ItemType %s cant calculate position" % (Item.getName(), Item.getType()))

        return 0.0, 0.0, 0.0
