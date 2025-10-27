from Foundation.Object.DemonObject import DemonObject


class ObjectAwards(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Open")
        Type.declareParam("Count")
        pass

    def _onParams(self, params):
        super(ObjectAwards, self)._onParams(params)
        self.initParam("Open", params, False)
        self.initParam("Count", params, 0)
