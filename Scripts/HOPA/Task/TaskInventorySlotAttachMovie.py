import Trace
from Foundation.Task.Task import Task

class TaskInventorySlotAttachMovie(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventorySlotAttachMovie, self)._onParams(params)
        self.Slot = params.get("Slot")
        self.Inventory = params.get("Inventory")
        self.MovieName = params.get("MovieName")

        pass

    def _onRun(self):
        if self.Inventory.isActive() is False:
            Trace.log("TaskInventorySlotAttachMovie", 3, "TaskInventorySlotAttachMovie._onRun-> Inventory hasn't Entity")
            return False
            pass

        pointSlot = self.Slot.getPoint()
        invItem = self.Slot.item

        if invItem is None:
            Trace.log("TaskInventorySlotAttachMovie", 3, "TaskInventorySlotAttachMovie._onRun-> Slot%d hasn't item" % (self.Slot.slotId))
            return True
            pass

        invItemEntity = invItem.getEntity()

        movie = self.Inventory.generateSlotMovie(self.MovieName, self.Slot.slotId)

        movieEntity = movie.getEntity()

        movieSlot = movieEntity.getMovieSlot("point")

        movieSlot.addChild(invItemEntity)
        pointSlot.addChild(movieEntity)

        return True
        pass
    pass