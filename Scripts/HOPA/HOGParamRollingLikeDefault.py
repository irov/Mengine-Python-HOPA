from HOGParamRolling import HOGParamRolling

class HOGParamRollingLikeDefault(HOGParamRolling):
    @staticmethod
    def hasHOGItemTextID(name, identity):
        item = HOGParamRollingLikeDefault.getHOGItem(name, identity)

        if item is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def getHOGItemTextID(name, identity):
        item = HOGParamRollingLikeDefault.getHOGItem(name, identity)

        return item.textID
        pass
    pass