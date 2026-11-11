from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionHintUse(ActionDefault):

    def _onCheck(self):
        return True
        pass

    def _onRun(self, source):
        source.addNotify(Notificator.onItemEffectEnd, self.ItemName)
