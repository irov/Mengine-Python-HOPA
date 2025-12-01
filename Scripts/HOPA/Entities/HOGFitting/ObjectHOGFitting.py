from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectHOGFitting(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("PrepareItems")
        Type.declareParam("Items")
        Type.declareParam("QueueItems")
        pass

    def _onParams(self, params):
        super(ObjectHOGFitting, self)._onParams(params)

        self.initParam("PrepareItems", params, [])
        self.initParam("Items", params, [])
        self.initParam("QueueItems", params, [])
        pass
