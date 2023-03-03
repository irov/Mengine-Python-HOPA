from Foundation.Object.DemonObject import DemonObject


class ObjectSpell(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "CurrentState")
        Type.addParam(Type, "IsValidUse")
        Type.addParam(Type, "AtmosphericUse")
        Type.addParam(Type, "HideState")
        pass

    def _onParams(self, params):
        super(ObjectSpell, self)._onParams(params)
        self.initParam("CurrentState", params, "Locked")
        self.initParam("IsValidUse", params, False)
        self.initParam("AtmosphericUse", params, False)
        self.initParam("HideState", params, "Idle")
        pass

    pass
