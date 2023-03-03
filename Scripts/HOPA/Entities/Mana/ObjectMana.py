from Foundation.Object.DemonObject import DemonObject


class ObjectMana(DemonObject):
    def _onParams(self, params):
        super(ObjectMana, self)._onParams(params)

        self.initParam("ManaCount", params, 0)
        self.initParam("HideState", params, "Idle")

        pass

    pass
