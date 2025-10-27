from Foundation.Object.DemonObject import DemonObject


class ObjectBalanceIndicator(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("ShowGold")
        Type.declareParam("ShowEnergy")
        Type.declareParam("ShowAdvertisement")

    def _onParams(self, params):
        super(ObjectBalanceIndicator, self)._onParams(params)

        self.initParam("ShowGold", params, True)
        self.initParam("ShowEnergy", params, True)
        self.initParam("ShowAdvertisement", params, True)
