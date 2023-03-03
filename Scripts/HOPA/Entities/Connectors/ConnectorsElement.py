class ConnectorsElement(object):
    def __init__(self, needCount, viewObject):
        self.stateObject = viewObject
        self.needCount = needCount
        self.count = 0
        # self.stateObject.setCurrentState("Off")
        pass

    def isHappy(self):
        if self.count == self.needCount:
            return True
            pass

        return False
        pass

    def incref(self):
        self.count += 1
        self.onUpdateCount()
        pass

    def decref(self):
        self.count -= 1
        self.onUpdateCount()
        pass

    def onUpdateCount(self):
        if self.count == self.needCount:
            self.stateObject.setCurrentState("On")
            pass
        else:
            self.stateObject.setCurrentState("Off")
            pass
        pass

    pass
