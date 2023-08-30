from Foundation.Object.DemonObject import DemonObject


class ObjectElementalMagic(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Element")

    def _onParams(self, params):
        super(ObjectElementalMagic, self)._onParams(params)

        self.initParam("Element", params, 0)

    def getPlayerElement(self):
        return self.getParam("Element")

    def setPlayerElement(self, element):
        return self.setParam("Element", element)
