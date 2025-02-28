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
        movie_name = self.movieObject.getName()
        movie_type = self.movieObject.getType()
        movie_group = self.movieObject.getGroup()
        task_name = "%s_PLAY" % movie_name

        if TaskManager.existTaskChain(task_name) is True:
            TaskManager.cancelTaskChain(task_name)

        with TaskManager.createTaskChain(Name=task_name, Group=movie_group) as tc:
            tc.addTask("TaskMovieLastFrame", MovieName=movie_name, Value=False)

            if movie_type == "ObjectMovie":
                tc.addTask("TaskMoviePlay", MovieName=movie_name)
            elif movie_type == "ObjectMovie2":
                tc.addTask("TaskMovie2Play", Movie2Name=movie_name)

            # tc.addTask("TaskMovieLastFrame", MovieName = name, Value = False)
            tc.addFunction(callback)
