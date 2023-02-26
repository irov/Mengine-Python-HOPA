class Cell(object):
    def __init__(self):
        self.element = None
        self.prevElement = None
        pass

    def __repr__(self):
        reprElement = self.element
        if self.element == None:
            reprElement = "None"
            pass

        reprPrev = self.prevElement
        if self.prevElement == None:
            reprPrev = "None"
            pass

        return "cell with element %s prev element %s" % (reprElement, reprPrev)
        pass

    def setElement(self, element):
        self.prevElement = self.element
        self.element = element
        pass

    def getElement(self):
        return self.element
        pass

    def getPrevElement(self):
        return self.prevElement
        pass
    pass

class Grid(object):
    def __init__(self, width, height):
        super(Grid, self).__init__()
        self.width = width
        self.height = height
        self.size = width * height
        self.area = [Cell() for i in range(self.size)]
        pass

    def getRow(self, index):
        start = self.width * index
        row = [self.area[i] for i in range(start, start + self.width)]
        return row
        pass

    def __repr__(self):
        result = ""
        for y in range(self.height):
            result += "|"
            row = self.getRow(y)
            for val in row:
                if val == None:
                    repr = "  None  "
                    pass
                else:
                    repr = str(val)
                    pass
                result += repr + "|"
            result += "\n\r"
            pass
        return result
        pass

    def getIndex(self, x, y):
        index = y * self.width + x
        return index
        pass

    def setCellValue(self, x, y, value):
        index = self.getIndex(x, y)
        cell = self.getCell(index)
        cell.setElement(value)
        pass

    def getCellValue(self, x, y):
        index = self.getIndex(x, y)
        cell = self.getCell(index)
        element = cell.getElement()
        return element
        pass

    def getCell(self, index):
        return self.area[index]
        pass

    def hasCell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            pass
        return True
        pass

    def moveCellValue(self, x, y, destX, destY, elementAfter):
        value = self.getCellValue(x, y)
        # print ("----",x,y,destX,destY,value)
        self.setCellValue(destX, destY, value)
        self.setCellValue(x, y, elementAfter)
        pass

    def visitElements(self, visitor, indexes):
        for index in indexes:
            if index < 0 or index >= self.size:
                pass
            cell = self.getCell(index)
            element = cell.getElement()
            visitor(index, element)
            pass
        pass
    pass