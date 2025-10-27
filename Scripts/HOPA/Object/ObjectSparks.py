from Foundation.Object.DemonObject import DemonObject


class ObjectSparks(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("State")

    def _onParams(self, params):
        super(ObjectSparks, self)._onParams(params)

        self.initParam("State", params, "Idle")
        pass

    pass
