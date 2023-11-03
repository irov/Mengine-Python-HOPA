from Foundation.Initializer import Initializer


# TODO  support onHover mode for chips

class ChipView(Initializer):
    def __init__(self):
        super(ChipView, self).__init__()
        self.states = None
        self.entity = None
        self.blockHover = False
        pass

    def prepare(self):
        def resetVisitor(stateObject, stateName):
            objects = stateObject.getObjects()
            for obj in objects:
                obj.setPosition((0, 0))
                pass
            pass

        self.entity.visitStates(resetVisitor)
        pass

    def setPosition(self, pos):
        self.states.setPosition(pos)
        pass

    def initHotSpot(self):
        self.hotSpot = Mengine.createNode("HotSpotPolygon")
        polygon = []
        polygon.append((0.0, 0.0))
        polygon.append((self.size.x, 0.0))
        polygon.append((self.size.x, self.size.y))
        polygon.append((0.0, self.size.y))
        self.hotSpot.setPolygon(polygon)
        self.hotSpot.enable()
        self.entity.addChild(self.hotSpot)
        # self.hotSpot.setInteractive(True)
        pass

    def updateSize(self):
        curState = self.states.getCurrentState()
        stateObject = self.states.getState(curState)
        objects = stateObject.getObjects()
        self.size = Mengine.vec2f(0, 0)
        for obj in objects:
            type = obj.getType()
            if type != "ObjectSprite":
                return
                pass

            spriteEntity = obj.getEntity()
            sprite = spriteEntity.getSprite()
            size = sprite.getSurfaceSize()
            if size.x > self.size.x:
                self.size.x = size.x
                pass
            if size.y > self.size.y:
                self.size.y = size.y
                pass
            pass
        pass

    def setBlockHover(self, block):
        self.blockHover = block
        pass

    def changeState(self, state):
        self.states.setCurrentState(state)
        self.updateSize()
        pass

    def _onInitialize(self, states):
        super(ChipView, self)._onInitialize(states)
        self.states = states
        self.entity = self.states.getEntity()
        self.prepare()
        self.changeState("Default")
        self.initHotSpot()
        pass

    def getEntity(self):
        return self.entity
        pass

    def _onFinalize(self):
        super(ChipView, self)._onFinalize()
        self.hotSpot.removeFromParent()
        Mengine.destroyNode(self.hotSpot)
        self.hotSpot = None
        pass

    def getSize(self):
        return self.size
        pass

    def getHotSpot(self):
        return self.hotSpot
        pass
