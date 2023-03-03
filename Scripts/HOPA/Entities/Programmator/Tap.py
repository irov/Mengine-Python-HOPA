class Tap(object):

    def __init__(self, nodeSlots):
        self.nodes = nodeSlots
        self.garbage = []
        self.cursor = None
        pass

    def push(self, Object):
        if self.cursor is None:
            self.cursor = 0
            pass
        else:
            self.cursor += 1
            pass

        Entity = Object.getEntity()
        current_node = self.nodes[self.cursor]
        current_node.addChild(Entity)
        Object.setPosition((0, 0))
        self.garbage.append(Entity)
        pass

    def flush(self):
        self.cursor = None
        for entity_garbage in self.garbage:
            entity_garbage.removeFromParent()
            pass
        self.garbage = []

        pass

    def isFull(self):
        return self.cursor >= len(self.nodes) - 1
        pass

    def onDeactivate(self):
        self.flush()
        self.cursor = None
        self.nodes = []
        pass

    pass
