from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionAddItem(ActionDefault):
    def _onParams(self, params):
        super(ActionAddItem, self)._onParams(params)
        self.itemName = params[0]
        pass

    def _onCheck(self):
        return True

    def _onRun(self):
        pass

    pass
