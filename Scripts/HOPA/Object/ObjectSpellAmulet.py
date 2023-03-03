from Foundation.Object.DemonObject import DemonObject


class ObjectSpellAmulet(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

    def _onParams(self, params):
        super(ObjectSpellAmulet, self)._onParams(params)

    def getSpellAmuletButton(self, power_type):
        if self.isActive():
            return self.entity.getSpellAmuletButton(power_type)

    def getSpellAmuletStoneByPower(self, power_name):
        if self.isActive():
            return self.entity.getSpellAmuletButtonByPower(power_name)

    def getAmulet(self):
        if self.isActive():
            return self.entity.getAmulet()

    def scopeOpenAmulet(self, source):
        amulet = self.getAmulet()

        if amulet is not None:
            source.addScope(amulet.scopeOpenAmulet)

    def scopeCloseAmulet(self, source):
        amulet = self.getAmulet()

        if amulet is not None:
            source.addScope(amulet.scopeCloseAmulet)

    def scopeSpellUIButtonValidClick(self, source):
        amulet = self.getAmulet()

        if amulet is not None:
            if amulet.getCurState() is amulet.HIDE:
                source.addScope(amulet.scopeOpenAmulet)

            else:
                source.addScope(amulet.scopeCloseAmulet)
