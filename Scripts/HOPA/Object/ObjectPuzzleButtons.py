from Foundation.Object.DemonObject import DemonObject


class ObjectPuzzleButtons(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Slot")
        pass

    def _onParams(self, params):
        super(ObjectPuzzleButtons, self)._onParams(params)

        self.initParam("Slot", params, None)
        pass
