from Foundation.Entity.BaseEntity import BaseEntity

class BonusItem(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "ItemsCount")
        pass

    def __init__(self):
        super(BonusItem, self).__init__()

        self.bonusList = None
        self.Text = None
        pass

    def getItemsCount(self):
        return self.object.getItemsCount()
        pass

    def setItemsCount(self, value):
        self.object.setItemsCount(value)
        pass

    def _increaseCount(self):
        ItemsCount = self.object.getItemsCount()
        ItemsCount += 1

        self.object.setItemsCount(ItemsCount)
        pass

    def _decreaseCount(self, value):
        ItemsCount = self.object.getItemsCount()
        if ItemsCount - value >= 0:
            ItemsCount -= value
            pass

        self.object.setItemsCount(ItemsCount)
        pass

    def _onActivate(self):
        super(BonusItem, self)._onActivate()

        self._preparation()
        pass

    def _preparation(self):
        MovieSlotObject = self.object.getObject("Movie_Slot")
        MovieSlotObject.setEnable(True)
        MovieEntity = MovieSlotObject.getEntity()

        self.MovieActiveCounterObject = self.object.getObject("Movie_ActiveCounter")
        MovieActiveCounterEntity = self.MovieActiveCounterObject.getEntity()

        self.MovieActiveCounterObject.setEnable(True)
        self.MovieActiveCounterObject.setPosition((0, 0))

        Slot = MovieEntity.getMovieSlot("slot")
        Slot.addChild(MovieActiveCounterEntity)

        Text_Count = MovieActiveCounterEntity.getMovieSlot("text")
        self.Text = self.object.getObject("Text_Count")
        self.Text.setTextID("ID_BonusItem")
        self.Text.setTextArgs(self.ItemsCount)

        self.Text.setEnable(True)
        self.Text.setPosition((0, 0))
        TextEntity = self.Text.getEntity()

        Text_Count.addChild(TextEntity)
        pass

    def _updateCount(self):
        self._increaseCount()
        self.Text.setText(u" X %d" % (self.ItemsCount,))
        pass

    def _onDeactivate(self):
        super(BonusItem, self)._onDeactivate()

        TextEntity = self.Text.getEntity()
        TextEntity.removeFromParent()

        MovieEntity = self.MovieActiveCounterObject.getEntity()
        MovieEntity.removeFromParent()
        pass
    pass