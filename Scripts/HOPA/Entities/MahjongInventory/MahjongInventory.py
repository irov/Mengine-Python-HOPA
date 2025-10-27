InventoryBase = Mengine.importEntity("InventoryBase")


class MahjongInventory(InventoryBase):
    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction("EnigmaName")
        Type.addAction("TextID", Update=MahjongInventory._updateTextMessage)

        Type.addActionActivate("ItemsCount", Update=MahjongInventory._updateItemsAllCount)
        Type.addActionActivate("FoundItems",
                               Append=MahjongInventory._appendFoundItems,
                               Update=MahjongInventory._updateFoundItems)

    def __init__(self):
        super(MahjongInventory, self).__init__()

    def _onActivate(self):
        super(MahjongInventory, self)._onActivate()

    def _onDeactivate(self):
        super(MahjongInventory, self)._onDeactivate()
        self.object.setEnigmaName(None)
        self.object.setTextID(None)
        self.object.setItemsCount(None)
        self.object.setFoundItems([])

    def _updateTextMessage(self, text_id):
        if self.object.hasObject("Text_Message") is False:
            return False
        text_message = self.object.getObject("Text_Message")

        if text_id is None:
            text_message.setEnable(False)
            return False

        text_message.setTextID(text_id)
        text_message.setEnable(True)

    def __updateItemsCount(self):
        if self.object.hasObject("Text_Count") is False:
            return False

        text_count = self.object.getObject("Text_Count")
        text_count.setTextArgs((len(self.FoundItems), self.ItemsCount))
        text_count.setEnable(True)
        return False

    def _updateItemsAllCount(self, value):
        self.__updateItemsCount()

    def _updateFound(self, value):
        self.__updateItemsCount()

    def _appendFoundItems(self, id, value):
        self._updateFound(value)

    def _updateFoundItems(self, list):
        if len(list) == 0:
            return

        for name in list:
            self._updateFound(name)

        self.__updateItemsCount()
