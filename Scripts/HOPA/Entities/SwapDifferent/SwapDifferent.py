from Foundation.TaskManager import TaskManager
from HOPA.SwapDifferentManager import SwapDifferentManager

from SwapDifferentElement import SwapDifferentElement


Enigma = Mengine.importEntity("Enigma")


def getMaxMin(first, second):
    if first > second:
        return (first, second)
        pass
    else:
        return (second, first)
        pass
    pass


class SwapDifferent(Enigma):
    def __init__(self):
        super(SwapDifferent, self).__init__()
        self.GameData = None
        self.leftBottomCorner = Mengine.vec2f(0, 0)
        self.elements = {}
        self.currentElement = None
        self.gridMovieName = "Movie_Grid"
        self.countElementsOnMove = -1
        pass

    def finalize(self):
        for elementId, element in self.elements.items():
            element.finalize()
            pass

        self.onFocusObserver = None
        self.elements = {}
        pass

    def _autoWin(self):
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _checkComplete(self):
        for elementId, element in self.elements.items():
            order = element.getOrder()
            check = self.GameData.rules[elementId]
            if order != check:
                return False
                pass
            pass

        self.enigmaComplete()
        return False

    def initLeftCorner(self):
        gridMovieObject = self.object.getObject(self.gridMovieName)
        entity = gridMovieObject.getEntity()

        slotLeft = entity.getMovieSlot("leftBottom")
        self.leftBottomCorner = slotLeft.getLocalPosition()
        pass

    def blockElements(self, value):
        for elementId, element in self.elements.items():
            element.setBlock(value)
            pass
        pass

    def initMovingElementsToCenter(self, minIndex, maxIndex):
        sortedByOrder = self.getSortedElements()
        # sorted(self.elements.values(), key = lambda el: el.getOrder() )
        first = sortedByOrder[minIndex].getPosition()
        last = sortedByOrder[maxIndex].getPosition()
        middle = first[0] + ((last[0] - first[0]) / 2)

        innerElements = sortedByOrder[minIndex: (maxIndex + 1)]
        for element in innerElements:
            pos = element.getPosition()
            element.addToMovingChain((middle, pos[1]))
            pass
        pass

    def playMovie(self):
        if TaskManager.existTaskChain("MovieSwapDifferent_onSwap"):
            return
            pass

        with TaskManager.createTaskChain(Name="MovieSwapDifferent_onSwap", Group=self.object) as tc:
            tc.addTask("TaskMoviePlay", MovieName="Movie_OnSwap", Loop=False)
            pass
        pass

    def swapElements(self, element1, element2):
        self.blockElements(True)

        order1 = element1.getOrder()
        order2 = element2.getOrder()
        maxIndex, minIndex = getMaxMin(order1, order2)
        self.initMovingElementsToCenter(minIndex, maxIndex)

        element1.setOrder(order2)
        element2.setOrder(order1)

        elements = self.getSortedElements()
        positions = self.calculatePositions(elements)
        for index, element in enumerate(elements):
            pos = positions[index]
            element.addToMovingChain(pos)
            pass

        def after():
            self.countElementsOnMove -= 1
            if self.countElementsOnMove > 0:
                return
                pass
            elif self.countElementsOnMove == 0:
                self.placeElements()
                self._checkComplete()
                self.blockElements(False)
                pass
            pass

        self.countElementsOnMove = len(elements)
        for element in elements:
            element.applyMovingChain(after)
            pass

        self.playMovie()
        pass

    def onClickElement(self, element):
        if self.currentElement is None:
            self.currentElement = element
            self.currentElement.setActive(True)
            pass

        elif self.currentElement is element:
            self.currentElement.setActive(False)
            self.currentElement = None
            pass
        else:
            self.currentElement.setActive(False)
            self.swapElements(self.currentElement, element)
            self.currentElement = None
            pass
        pass

    def calculatePositions(self, elements):
        positions = []
        point = Mengine.vec2f(self.leftBottomCorner.x, self.leftBottomCorner.y)
        for element in elements:
            size = element.getSize()
            locationY = point.y - size.y
            locationX = point.x
            positions.append((locationX, locationY))
            point.x += size.x
            pass

        return positions
        pass

    def getSortedElements(self):
        sortedByOrder = sorted(self.elements.values(), key=lambda el: el.getOrder())
        return sortedByOrder
        pass

    def placeElements(self):
        elements = self.getSortedElements()
        positions = self.calculatePositions(elements)
        for index, element in enumerate(elements):
            pos = positions[index]
            element.setPosition(pos)
            pass
        pass

    def _onActivate(self):
        super(SwapDifferent, self)._onActivate()
        self.GameData = SwapDifferentManager.getGame(self.EnigmaName)

        self.initLeftCorner()

        for elementId, elementData in self.GameData.elements.items():
            statesObject = self.object.getObject(elementData["ObjectName"])
            element = SwapDifferentElement(statesObject)
            element.setOrder(elementData["StartOrder"])
            self.elements[elementId] = element
            pass

        self.placeElements()
        pass

    def _playEnigma(self):
        for elementId, element in self.elements.items():
            element.initialize(self.onClickElement)
            pass
        pass

    pass
