from Foundation.Object.DemonObject import DemonObject

class ObjectCollectedMapIndicator(DemonObject):
    def _onParams(self, params):
        super(ObjectCollectedMapIndicator, self)._onParams(params)
        self.initParam("CurrentValue", params, 0)
        self.initParam("CurrentCollectedMap", params, None)

        pass
    pass