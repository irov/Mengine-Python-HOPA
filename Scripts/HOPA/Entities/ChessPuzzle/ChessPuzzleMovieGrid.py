from Foundation.TaskManager import TaskManager


class ChessPuzzleMovieGrid(object):
    def __init__(self, group, grid, description):
        movieObj = group.getObject(description.objectName)
        self.movie = movieObj.getEntity()
        self.slots = {}
        self.grid = grid
        self.collectSlots(description)
        pass

    def getIndex(self, x, y):
        index = y * self.grid.width + x
        return index
        pass

    def getSlot(self, x, y):
        index = self.getIndex(x, y)
        slot = self.slots[index]
        return slot
        pass

    def setNode(self, x, y, node):
        slot = self.getSlot(x, y)
        slot.addChild(node)
        pass

    def moveNode(self, x, y, node, movie, callback):
        taskName = "%i_%i_PLAY" % (x, y)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        def after():
            node.removeFromParent()
            movieEntity.removeFromParent()
            self.setNode(x, y, node)
            callback()
            pass

        slot = node.getParent()
        movieEntity = movie.getEntity()

        slideSlot = movieEntity.getMovieSlot("move")
        slideSlot.addChild(node)
        slot.addChild(movieEntity)

        with TaskManager.createTaskChain(Name=taskName, Group=None) as tc:
            tc.addTask("TaskMoviePlay", Movie=movie)
            tc.addFunction(after)
            pass
        pass

    def collectSlots(self, description):
        for cell in description.cells:
            index = self.getIndex(cell['x'], cell['y'])
            slotName = cell['slotName']
            slot = self.movie.getMovieSlot(slotName)
            self.slots[index] = slot
            pass
        pass

    def refresh(self):
        def visitor(element):
            if element is None:
                return
                pass
            x = element.getX()
            y = element.getY()
            slot = self.getSlot(x, y)
            node = element.getNode()
            node.removeFromParent()
            slot.addChild(node)
            pass

        self.grid.visitElements(visitor)
        pass
