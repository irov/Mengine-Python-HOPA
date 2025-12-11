InventoryBase = Mengine.importEntity("InventoryBase")


class HOGInventoryCount(InventoryBase):
    def __init__(self):
        super(HOGInventoryCount, self).__init__()

    @staticmethod
    def declareORM(type_):
        InventoryBase.declareORM(type_)

        type_.addAction("HOG")

        type_.addAction('EnigmaName')
        type_.addAction('TextID', Update=HOGInventoryCount._updateTextMessage)

        type_.addActionActivate("ItemsCount", Update=HOGInventoryCount._updateItemsAllCount)
        type_.addActionActivate("FindItems",
                                Append=HOGInventoryCount._appendFindItems,
                                Update=HOGInventoryCount._updateFindItems)
        type_.addActionActivate("FoundItems",
                                Append=HOGInventoryCount._appendFoundItems,
                                Update=HOGInventoryCount._updateFoundItems)

    def _onActivate(self):
        super(HOGInventoryCount, self)._onActivate()

    def _onDeactivate(self):
        super(HOGInventoryCount, self)._onDeactivate()
        self.object.setHOG(None)
        self.object.setEnigmaName(None)
        self.object.setTextID(None)
        self.object.setItemsCount(None)
        self.object.setFindItems([])
        self.object.setFoundItems([])

    def _updateTextMessage(self, text_id):
        text_message = self.object.getObject("Text_Message")

        if text_id is None:
            text_message.setEnable(False)
            return
        text_message.setTextID(text_id)
        text_message.setEnable(True)

    def _updateItemsAllCount(self, value):
        self.__updateItemsCount()

    def __updateItemsCount(self):
        if self.object.hasObject("Text_Count") is False:
            return False

        text_count = self.object.getObject("Text_Count")
        text_count.setTextArgs((len(self.FoundItems), self.ItemsCount))
        text_count.setEnable(True)
        return False

    def _appendFindItems(self, id_, names_list):
        pass

    def _updateFindItems(self, list_):
        pass

    def _appendFoundItems(self, id, value):
        self._updateFound(value)

    def _updateFoundItems(self, list):
        if len(list) == 0:
            return

        for name in list:
            self._updateFound(name)

        self.__updateItemsCount()

    def _updateFound(self, value):
        self.__updateItemsCount()
