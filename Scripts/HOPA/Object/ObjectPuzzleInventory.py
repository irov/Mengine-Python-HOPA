from Foundation.Object.DemonObject import DemonObject

class ObjectPuzzleInventory(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "TextID")
        Type.addParam(Type, "EnigmaName")

    def _onParams(self, params):
        super(ObjectPuzzleInventory, self)._onParams(params)
        self.initParam("TextID", params, None)
        self.initParam("EnigmaName", params, None)