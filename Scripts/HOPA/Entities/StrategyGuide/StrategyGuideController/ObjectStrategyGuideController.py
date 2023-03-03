from Foundation.Object.DemonObject import DemonObject


class ObjectStrategyGuideController(DemonObject):
    def _onParams(self, params):
        super(ObjectStrategyGuideController, self)._onParams(params)
        self.initParam("CurrentPage", params, 1)
        pass

    pass
