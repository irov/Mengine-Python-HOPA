from Foundation.Object.DemonObject import DemonObject


class ObjectProfile(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Accounts")
        Type.addParam(Type, "Current")
        Type.addConst(Type, "MaxCount")
        pass

    def _onParams(self, params):
        super(ObjectProfile, self)._onParams(params)

        self.initParam("Accounts", params, [])
        self.initParam("Current", params, None)
        self.initConst("MaxCount", params, 5)
        pass

    def getSlotID(self, _accountID):
        Accounts = self.getParam("Accounts")

        for slotID, accountID in Accounts:
            if accountID == _accountID:
                return slotID
                pass
            pass

        return None
        pass

    def getAccountID(self, _slotID):
        Accounts = self.getParam("Accounts")

        for slotID, accountID in Accounts:
            if slotID == _slotID:
                return accountID
                pass
            pass

        return None
        pass

    def getEmptySlotID(self):
        Accounts = self.getParam("Accounts")

        Slots = [slotID for slotID, accountID in Accounts]

        MaxCount = self.getMaxCount()
        for slotID in xrange(MaxCount):
            if slotID not in Slots:
                return slotID
                pass
            pass

        return None
        pass

    pass
