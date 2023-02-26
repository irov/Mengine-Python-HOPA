from Foundation.Object.DemonObject import DemonObject

class ObjectInventoryItemAccumulate(DemonObject):
    def _onParams(self, params):
        super(ObjectInventoryItemAccumulate, self)._onParams(params)
        self.initParam("Value", params, 0)
        self.initParam("FoundItems", params, [])
        pass
    pass

    # def hasItem(self, ItemName):
    #     FoundItems = self.getParam("FoundItems")
    #
    #     if ItemName not in FoundItems:
    #         return False
    #         pass
    #
    #     return True
    #     pass

    def reduceValue(self, value):
        Value = self.getParam("Value")
        new = Value - value
        if new > 0:
            self.setParam("Value", new)
            return "back"
            pass
        elif new == 0:
            self.setParam("Value", 0)
            return "take"
            pass
        else:
            return "invalid"
            pass
        pass
    pass