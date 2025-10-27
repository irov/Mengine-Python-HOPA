from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectColorCollect(ObjectEnigma):

    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("BulbAction")
        pass

    def _onParams(self, params):
        super(ObjectColorCollect, self)._onParams(params)
        self.initParam("BulbAction", params, False)
        pass
