class Partition(object):
    def __init__(self, orderedNodes):
        self.nodes = orderedNodes
        self.depth = len(orderedNodes) - 1
        self.cursor = None
        self.nodeToChild = {}
        self.lastHold = False
        pass

    def getOrderedChilds(self):
        ordered_childs = [self.nodeToChild.get(node) for node in self.nodes]
        return ordered_childs
        pass

    def take(self):
        if self.cursor is None:
            return
            pass

        top_node = self.nodes[self.cursor]
        if self.cursor == 0:
            self.cursor = None
        else:
            self.cursor -= 1
        children = self.nodeToChild[top_node]
        children.removeFromParent()
        del self.nodeToChild[top_node]
        return children
        pass

    def give(self, children):
        self.lastHold = False
        if self.cursor is None:
            self.cursor = 0
        elif self.cursor >= self.depth:
            return
            pass
        else:
            self.cursor += 1

        top_node = self.nodes[self.cursor]
        top_node.addChild(children)

        children_object = children.getObject()
        children_object.setPosition((0, 0))
        self.nodeToChild[top_node] = children
        pass

    def getState(self):
        return self.cursor
        pass

    def isFull(self):
        return self.cursor >= self.depth
        pass

    def onDeactivate(self):
        for child in self.nodeToChild.values():
            child.removeFromParent()
            pass

        self.nodeToChild = {}
        self.cursor = None
        self.nodes = []
        pass

    def isEmpty(self):
        return self.cursor is None
        pass

    def getDepth(self):
        return self.depth + 1
        pass

    def isFinal(self):
        return self.depth == 2
        pass


class FinalPartition(object):
    # Aggregation object of partition for win check

    def __init__(self, chosenPartitionInstance, wheelInstance):
        self.partition = chosenPartitionInstance
        self.wheel = wheelInstance
        self.win_order = []
        self.current_down = 0
        self.initState = chosenPartitionInstance.getState()
        pass

    def onDeactivate(self):
        self.wheel = None
        self.partition = None
        self.initState = None
        pass

    def setWinOrder(self, orderedNameMovieList):
        self.win_order = orderedNameMovieList
        pass

    def checkWin(self, embed_method):
        cur_state = self.partition.getState()

        self.initState = cur_state
        nodes = self.partition.nodes

        matches = 0
        if len(nodes) != len(self.win_order):
            return False
            pass

        childrensOrder = self.partition.getOrderedChilds()
        nodesChildObjects = [nc.getObject() for nc in childrensOrder if nc is not None]
        childNames = [nco.getName() for nco in nodesChildObjects]

        for i, child in enumerate(childNames):
            if child == self.win_order[i]:
                matches += 1
                pass
            pass

        if len(childNames) == matches:
            self.partition.lastHold = True
            pass

        if matches > self.current_down:
            self.updateView(finalMethod=embed_method)
            self.current_down = matches
            pass

        elif matches < self.current_down:
            self.updateView(True)
            self.current_down = matches
            pass

        if childNames == self.win_order:
            return True
            pass
        else:
            return False
            pass
        pass

    def updateView(self, up=False, finalMethod=None):
        if up is True:
            self.wheel.moveUp()
            return
            pass
        self.wheel.moveDown(finalMethod)
        pass
