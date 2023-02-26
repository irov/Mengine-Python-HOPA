from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectHOGFitting(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectHOGFitting, self)._onParams(params)

        self.initParam("PrepareItems", params, [])
        self.initParam("Items", params, [])
        self.initParam("QueueItems", params, [])
        pass

    pass