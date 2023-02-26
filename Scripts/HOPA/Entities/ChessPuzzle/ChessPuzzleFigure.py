from ChessPuzzleElement import ChessPuzzleElement

class ChessPuzzleFigure(ChessPuzzleElement):
    def __init__(self, type):
        super(ChessPuzzleFigure, self).__init__()
        self.figureType = type
        self.placed = False
        pass

    def initialize(self, states):
        self.states = states
        entity = states.getEntity()

        def resetVisitor(stateObject, stateName):
            objects = stateObject.getObjects()
            for obj in objects:
                obj.setPosition((0, 0))
                spriteEntity = obj.getEntity()
                sprite = spriteEntity.getSprite()
                size = sprite.getSurfaceSize()
                sprite.setLocalPosition((-size.x / 2, -size.y / 2))
                pass
            pass

        entity.visitStates(resetVisitor)
        self.node = entity
        self.updateView()
        pass

    def getFigureType(self):
        return self.figureType
        pass

    def setPlaced(self, placed):
        self.placed = placed
        pass

    def _updateView(self):
        if self.placed == True:
            self.states.setCurrentState("Complete")
            pass
        else:
            self.states.setCurrentState("Default")
            pass
        pass

    def isPlaced(self):
        return self.placed
        pass

    def isCanMove(self, dx, dy, nextElement):
        if nextElement != None:
            return False
            pass
        return True
        pass

    def __repr__(self):
        return "F->" + str(self.figureType)
        pass
    pass