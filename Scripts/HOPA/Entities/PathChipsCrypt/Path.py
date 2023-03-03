class PathPoint(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value
        self.connect = {}
        pass

    def __repr__(self):
        return "<Slot with id " + str(self.id) + " value :" + str(self.value) + ">"
        pass

    def setConnect(self, slotName, value):
        self.connect[slotName] = value
        pass

    def removeConnect(self, slotName):
        del self.connect[slotName]
        pass

    def isConnect(self, slotName):
        state = slotName in self.connect
        return state


class Path(object):
    slots = {}

    @staticmethod
    def addSlot(name, value):
        Path.slots[name] = PathPoint(name, value)
        pass

    @staticmethod
    def hasSlot(name):
        return name in Path.slots
        pass

    @staticmethod
    def getSlot(name):
        return Path.slots[name]
        pass

    @staticmethod
    def getSlotValue(name):
        slot = Path.getSlot(name)
        return slot.value
        pass

    @staticmethod
    def setSlotValue(name, value):
        slot = Path.getSlot(name)
        slot.value = value
        pass

    @staticmethod
    def connect(slotName1, slotName2, value):
        slot1 = Path.getSlot(slotName1)
        slot2 = Path.getSlot(slotName2)
        slot1.setConnect(slotName2, value)
        slot2.setConnect(slotName1, value)
        pass

    @staticmethod
    def isConnectedSlots(slotName1, slotName2):
        slot1 = Path.getSlot(slotName1)
        slot2 = Path.getSlot(slotName2)

        if slot1.isConnect(slotName2) is False:
            return False
            pass

        if slot2.isConnect(slotName1) is False:
            return False
            pass

        return True
        pass

    pass

    @staticmethod
    def move(slotNameFrom, slotNameTo):
        if Path.canMove(slotNameFrom, slotNameTo) is False:
            return False
            pass

        slotFrom = Path.getSlot(slotNameFrom)
        slotTo = Path.getSlot(slotNameTo)

        slotTo.value = slotFrom.value
        slotFrom.value = None
        pass

    @staticmethod
    def swapSlots(slotNameFrom, slotNameTo):
        slotFrom = Path.getSlot(slotNameFrom)
        slotTo = Path.getSlot(slotNameTo)
        temp = slotTo.value
        slotTo.value = slotFrom.value
        slotFrom.value = temp
        pass

    @staticmethod
    def getActiveConnects(slotNameFrom):
        slot = Path.getSlot(slotNameFrom)
        activeConnects = []
        # print "-----"
        # print slotNameFrom
        # print slot.connect
        # print slotNameFrom
        for slotNameTo, connection in slot.connect.items():
            if Path.canMove(slotNameFrom, slotNameTo) is True:
                activeConnects.append((slotNameTo, connection))
                pass
            pass

        return activeConnects
        pass

    @staticmethod
    def getConnects(slotNameFrom):
        slot = Path.getSlot(slotNameFrom)
        Connects = []
        for slotNameTo, connection in slot.connect.items():
            Connects.append((slotNameTo, connection))
            pass
        return Connects
        pass

    @staticmethod
    def canMove(slotNameFrom, slotNameTo):
        slotFrom = Path.getSlot(slotNameFrom)
        slotTo = Path.getSlot(slotNameTo)

        if slotFrom.value == None:
            # print (slotFrom,"value None")
            return False
            pass

        if slotTo.value != None:
            # print (slotTo,"value  not None")
            return False
            pass

        if Path.isConnectedSlots(slotNameFrom, slotNameTo) is False:
            # print (slotNameFrom,slotNameTo,"not connected")
            return False
            pass

        return True
        pass

    pass


"""
Path.addSlot("slot0",0)
Path.addSlot("slot1",1)
Path.addSlot("slot2",2)
Path.addSlot("slot3",None)
Path.addSlot("slot4",4)

Path.connect("slot0","slot1")
Path.connect("slot1","slot2")
Path.connect("slot2","slot3")
Path.connect("slot3","slot4")
Path.connect("slot4","slot0")


print (Path.canMove("slot1","slot3"))
print (Path.canMove("slot3","slot2"))
print (Path.canMove("slot2","slot3"))
Path.move("slot2","slot3")
print (Path.canMove("slot3","slot2"))
Path.move("slot3","slot2")
print(Path.slots)
"""
