from Foundation.Object.DemonObject import DemonObject


class ObjectSpell(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("CurrentState")
        Type.declareParam("IsValidUse")
        Type.declareParam("AtmosphericUse")
        Type.declareParam("HideState")
        pass

    def _onParams(self, params):
        super(ObjectSpell, self)._onParams(params)
        self.initParam("CurrentState", params, "Locked")
        self.initParam("IsValidUse", params, False)
        self.initParam("AtmosphericUse", params, False)
        self.initParam("HideState", params, "Idle")
        pass

    pass
