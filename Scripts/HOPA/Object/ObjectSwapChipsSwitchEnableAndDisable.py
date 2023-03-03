from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectSwapChipsSwitchEnableAndDisable(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, 'visibleChipsParam')
        Type.addParam(Type, 'finishFlag')

    def _onParams(self, params):
        super(ObjectSwapChipsSwitchEnableAndDisable, self)._onParams(params)
        self.initParam('visibleChipsParam', params, {})
        self.initParam('finishFlag', params, False)

    def getVisibleChips(self):
        return self.getParam('visibleChipsParam')

    def setVisibleChips(self, slotID, typeChip):
        visibleChips = self.getParam('visibleChipsParam')
        visibleChips[slotID] = typeChip
        self.setParam('visibleChipsParam', visibleChips)
