from Foundation.Object.DemonObject import DemonObject


class ObjectInventoryItemAccumulate(DemonObject):
    def _onParams(self, params):
        super(ObjectInventoryItemAccumulate, self)._onParams(params)
        self.initParam("Value", params, 0)
        self.initParam("FoundItems", params, [])

    def reduceValue(self, value):
        Value = self.getParam("Value")
        new = Value - value
        if new > 0:
            self.setParam("Value", new)
            return "back"
        elif new == 0:
            self.setParam("Value", 0)
            return "take"
        else:
            return "invalid"
