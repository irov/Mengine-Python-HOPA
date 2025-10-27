InventoryBase = Mengine.importEntity("InventoryBase")


class PuzzleInventory(InventoryBase):
    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction("TextID", Update=PuzzleInventory._updateTextID)
        Type.addAction("EnigmaName")

    def __init__(self):
        super(PuzzleInventory, self).__init__()

    def _onActivate(self):
        super(PuzzleInventory, self)._onActivate()

    def _onDeactivate(self):
        super(PuzzleInventory, self)._onDeactivate()
        self.object.setEnigmaName(None)
        self.object.setTextID(None)

    def _updateTextID(self, textID):
        Text_Message = self.object.getObject("Text_Message")

        if textID is None:
            Text_Message.setEnable(False)
            return
        Text_Message.setTextID(textID)
        Text_Message.setEnable(True)
