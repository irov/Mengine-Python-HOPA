from Foundation.TaskManager import TaskManager
from Functor import Functor


class SwapDifferentElement(object):
    def __init__(self, states):
        super(SwapDifferentElement, self).__init__()
        self.states = states
        self.entity = self.states.getEntity()
        self.size = Mengine.vec2f(0, 0)
        self.order = None
        self.changeState("Default")
        self.updateSize()
        self.block = False
        self.movingChain = []
        pass

    def addToMovingChain(self, point):
        self.movingChain.append(point)
        pass

    def clearMovingChain(self):
        self.movingChain = []
        pass

    def applyMovingChain(self, callback):
        if len(self.movingChain) == 0:
            callback()
            return
            pass

        name = self.states.getName()
        taskName = "%s_MOVING" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        group = self.states.getGroup()
        with TaskManager.createTaskChain(Name=taskName, Group=group) as tc:
            for point in self.movingChain:
                time = 0.5
                time *= 1000  # speed fix
                tc.addTask("TaskNodeMoveTo", Node=self.entity, Time=time, To=point)
                pass

            tc.addFunction(self.clearMovingChain)
            tc.addFunction(callback)
            pass
        pass

        pass

    def setPosition(self, position):
        self.states.setPosition(position)
        pass

    def getPosition(self):
        return self.states.getPosition()
        pass

    def getOrder(self):
        return self.order
        pass

    def setOrder(self, order):
        self.order = order
        pass

    def getSize(self):
        return self.size
        pass

    def initialize(self, callback):
        self.initStates()
        self.initHotSpot(callback)
        pass

    def finalize(self):
        self.hotSpot.removeFromParent()
        Mengine.destroyNode(self.hotSpot)
        self.hotSpot = None
        pass

    def initHotSpot(self, callback):
        self.hotSpot = Mengine.createNode("HotSpotPolygon")
        polygon = []
        polygon.append((0.0, 0.0))
        polygon.append((self.size.x, 0.0))
        polygon.append((self.size.x, self.size.y))
        polygon.append((0.0, self.size.y))

        self.hotSpot.setPolygon(polygon)
        self.hotSpot.enable()
        self.hotSpot.setEventListener(onHandleMouseButtonEvent=Functor(self._onMouseButtonEvent, callback))
        self.entity.addChild(self.hotSpot)
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

    def setActive(self, value):
        if value is True:
            self.changeState("Active")
            pass
        else:
            self.changeState("Default")
            pass
        pass

    def changeState(self, state):
        self.states.setCurrentState(state)
        self.updateSize()
        pass

    def setBlock(self, state):
        self.block = state
        pass

    def isBlock(self):
        return self.block
        pass

    def _onMouseButtonEvent(self, touchId, x, y, button, isDown, isPressed, callback):
        if self.isBlock() is True:
            return False
            pass
        if hs != self.hotSpot:
            return False
            pass

        if button != 0:
            return False
            pass

        if isDown is False:
            return False
            pass

        callback(self)
        return False
        pass
