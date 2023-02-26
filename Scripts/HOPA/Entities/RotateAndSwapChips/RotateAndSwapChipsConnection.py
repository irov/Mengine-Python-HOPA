from Foundation.TaskManager import TaskManager

class RotateAndSwapChipsConnection(object):
    def __init__(self, movieObject):
        self.movieObject = movieObject
        self.movie = movieObject.getEntity()
        self.slots = {}
        pass

    def setSlotIdentity(self, slotId, slotName):
        self.slots[slotId] = slotName
        pass

    def attachToSlot(self, slotId, chip):
        slotName = self.slots[slotId]
        slot = self.movie.getMovieSlot(slotName)
        chip.attachTo(slot)
        pass

    def hasSlot(self, slotId):
        return slotId in self.slots
        pass

    def move(self, callback):
        name = self.movieObject.getName()
        taskName = "%s_PLAY" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        group = self.movieObject.getGroup()
        with TaskManager.createTaskChain(Name=taskName, Group=group) as tc:
            tc.addTask("TaskMovieLastFrame", MovieName=name, Value=False)
            tc.addTask("TaskMoviePlay", MovieName=name)
            # tc.addTask("TaskMovieLastFrame", MovieName = name, Value = False)
            tc.addTask("TaskFunction", Fn=callback)
            pass
        pass
    pass