from HOPA.Entities.InventoryFX.ActionDefaultRemove import ActionDefaultRemove

class ActionRemoveItem(ActionDefaultRemove):
    def _onCheck(self):
        return True
        pass

    def _onSkip(self):
        pass

    def _onRun(self):
        pass
    pass