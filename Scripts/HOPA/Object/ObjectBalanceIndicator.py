from Foundation.Object.DemonObject import DemonObject


class ObjectBalanceIndicator(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "ShowGold")
        Type.addParam(Type, "ShowEnergy")
        Type.addParam(Type, "ShowAdvertisement")

    def _onParams(self, params):
        super(ObjectBalanceIndicator, self)._onParams(params)

        self.initParam("ShowGold", params, True)
        self.initParam("ShowEnergy", params, True)
        self.initParam("ShowAdvertisement", params, True)
