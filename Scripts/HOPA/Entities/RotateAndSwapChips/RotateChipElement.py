from Functor import Functor


class RotateChipElement(object):
    RADIAN = 57.295779513

    def __init__(self, statesObject, needSlot, needAngle):
        self.slotId = None
        self.entity = statesObject.getEntity()
        self.entity_node = statesObject.getEntityNode()
        self.states = statesObject

        self.block = False

        self.needSlot = needSlot
        self.needAngle = needAngle

        self.states.setCurrentState("Default")
        # self.rotationNode =  Mengine.createNode("Interender")

        # self.rotationNode =  Mengine.createNode("Interender")
        self.rotationNode = Mengine.createNode("Interender")
        self.rotationNode.setName("rotationNode")

        self.rotationNode.compile()
        self.rotationNode.enable()

        self.rotationNode.addChild(self.entity_node)

        # self.updateSize()
        # print "init",self.rotationNode,self.entity,self.rotationNode.getLocalPosition().x,self.rotationNode.getLocalPosition().y,self.rotationNode.getLocalPosition().z
        pass

    def initStates(self):
        def resetVisitor(stateObject, stateName):
            objects = stateObject.getObjects()
            for obj in objects:
                obj.setPosition((0, 0))
                pass
            pass

        self.entity.visitStates(resetVisitor)
        pass

    def initHotSpot(self, callback):
        self.hotSpot = Mengine.createNode("HotSpotPolygon")
        polygon = []
        polygon.append((0.0, 0.0))
        polygon.append((self.size.x, 0.0))
        polygon.append((self.size.x, self.size.y))
        polygon.append((0.0, self.size.y))

        self.hotSpot.setPolygon(polygon)
        self.hotSpot.setEventListener(onHandleMouseButtonEvent=Functor(self._onMouseButtonEvent, callback))
        self.entity.addChild(self.hotSpot)
        pass

    def initialize(self, callback):
        self.initStates()
        self.initHotSpot(callback)
        pass

    def finalize(self):
        self.hotSpot.removeFromParent()
        Mengine.destroyNode(self.hotSpot)
        self.hotSpot = None

        self.rotationNode.removeFromParent()
        self.entity.removeFromParent()
        pass

    def attachTo(self, node):
        self.updateSize()
        node.addChild(self.rotationNode)
        pass

    def setSlotId(self, slotId):
        self.slotId = slotId
        self.updateState()
        pass

    def getSlotId(self):
        return self.slotId
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
        self.rotationNode.setOrigin((self.size.x / 2, self.size.y / 2))
        pass

    def setRotate(self, value):
        if value is True:
            self.changeState("Rotate")
            pass
        else:
            self.updateState()
            pass
        pass

    def setActive(self, value):
        if value is True:
            self.changeState("Active")
            pass
        else:
            self.updateState()
            pass
        pass

    def changeState(self, state):
        self.states.setCurrentState(state)
        self.updateSize()
        pass

    def updateState(self):
        if self.isComplete() is True:
            self.changeState("Complete")
            pass
        else:
            self.changeState("Default")
            pass
        pass

    def isComplete(self):
        if self.slotId != self.needSlot:
            return False
            pass

        angle = self.getAngleInDegree()

        if abs(Mengine.angle_delta_deg(angle, self.needAngle)) > 0.001:
            return False
            pass

        return True
        pass

    def setBlock(self, state):
        self.block = state
        pass

    def isBlock(self):
        return self.block
        pass

    def _onMouseButtonEvent(self, context, event, callback):
        if self.isBlock() is True:
            return False

        if event.button != Mengine.MC_LBUTTON:
            return False

        if event.isDown is False:
            return False

        callback(self)

        return False

    def setAngleInDegree(self, angle):
        angleRadian = angle / RotateChipElement.RADIAN
        self.rotationNode.setAngle(angleRadian)
        pass

    def rotateOnAngleInDegree(self, deltaAngle):
        angleRadian = deltaAngle / RotateChipElement.RADIAN
        angle = self.rotationNode.getAngle()
        resultAngle = angle + angleRadian
        self.rotationNode.setAngle(resultAngle)
        pass

    def getAngleInDegree(self):
        angle = self.rotationNode.getAngle()
        angle *= RotateChipElement.RADIAN
        return angle
        pass

    pass
