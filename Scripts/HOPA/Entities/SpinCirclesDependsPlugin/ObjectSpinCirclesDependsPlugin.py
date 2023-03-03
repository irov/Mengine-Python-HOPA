from Foundation.Object.DemonObject import DemonObject


class ObjectSpinCirclesDependsPlugin(DemonObject):
    def _onParams(self, params):
        super(ObjectSpinCirclesDependsPlugin, self)._onParams(params)
        self.initParam("StoreData", params, {})
        pass

    pass
