class SegmentSlot(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value
        pass

    def __repr__(self):
        return "%i-%i" % (self.id, self.value)
        pass


class Segment(object):
    def __init__(self, elements):
        self.elements = elements
        pass

    def getElements(self):
        return self.elements
        pass

    def isUniqueValue(self, value):
        for element in self.elements:
            # print "isUniqueValue",value,element.value,element.id
            if element.value != value:
                return False
                pass
            pass
        return True
        pass

    def get(self, index):
        return self.elements[index]
        pass

    def getValues(self):
        values = []
        for slot in self.elements:
            values.append(slot.value)
            pass
        return Segment(values)
        pass

    def setValues(self, values):
        for index, value in enumerate(values.elements):
            self.elements[index].value = value
            pass
        pass

    def getLast(self):
        element = self.elements[len(self.elements) - 1]
        return element
        pass

    def getFirst(self):
        element = self.elements[0]
        return element
        pass

    def popLast(self):
        element = self.elements.pop()
        return element
        pass

    def popFirst(self):
        element = self.elements.pop(0)
        return element
        pass

    def pushBack(self, element):
        self.elements.append(element)
        pass

    def pushFront(self, element):
        self.elements.insert(0, element)
        pass

    def __repr__(self):
        return self.elements.__repr__()
