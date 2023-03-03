from Foundation.Object.DemonObject import DemonObject


class ObjectInventoryBase(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

    def _onParams(self, params):
        super(ObjectInventoryBase, self)._onParams(params)
