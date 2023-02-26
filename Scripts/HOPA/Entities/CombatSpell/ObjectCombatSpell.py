from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectCombatSpell(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectCombatSpell, self)._onParams(params)
        self.initParam("FieldWidth", params)
        self.initParam("FieldHeight", params)
        self.initParam("StartAiCount", params)
        self.initParam("StartPlayerCount", params)

        self.initParam("FieldXY", params, [])
        self.initParam("AITurn", params, False)
        self.initParam("CheckWin", params, False)
        pass
    pass