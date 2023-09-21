from Foundation.TaskManager import TaskManager


class ChipsMoving(object):
    def __init__(self, movie, slotFrom, slotTo, soundMovieName):
        self.movieObject = movie
        self.movie = movie.getEntity()
        self.slotFrom = slotFrom
        self.slotTo = slotTo
        self.movieData = {}
        self.getMovieData()
        self.movieSlot = self.movie.getMovieSlot("move")
        self.currentIndex = -1
        self.lastIndex = len(self.movieData) - 1
        self.soundMovieName = soundMovieName
        pass

    def __repr__(self):
        return "ChipsMoving From %i To %i index %i last %i" % (self.slotFrom, self.slotTo, self.currentIndex, self.lastIndex)
        pass

    def getSlotPosition(self, slot):
        index = None
        if slot == self.slotFrom:
            index = 0
            pass
        elif slot == self.slotTo:
            index = self.lastIndex
            pass
        else:
            return None
            pass

        point = self.movieData[index]
        return point['position']
        pass

    def goTo(self, slot):
        if slot == self.slotFrom:
            self.setFrame(0)
            pass
        elif slot == self.slotTo:
            self.setFrame(self.lastIndex)
            pass
        else:
            pass
        pass

    def playTo(self, slot, callback):
        if slot == self.slotFrom:
            self.playBackward(callback)
            pass
        elif slot == self.slotTo:
            self.playForward(callback)
            pass
        else:
            pass
        pass

    def playForward(self, callback):
        name = self.movieObject.getName()
        taskName = "%s_PLAY_FORWARD" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        group = self.movieObject.getGroup()
        with TaskManager.createTaskChain(Name=taskName, Group=group) as tc:
            with tc.addParallelTask(2) as (tc_chip, tc_sound):
                tc_chip.addTask("TaskMovieReverse", MovieName=name, Reverse=False)
                tc_chip.addTask("TaskMoviePlay", MovieName=name)
                # tc_chip.addTask("TaskMovieLastFrame", MovieName = name, Value = True)
                tc_chip.addTask("TaskFunction", Fn=callback)

                tc_sound.addTask("TaskMoviePlay", MovieName=self.soundMovieName)
            pass
        pass

    def playBackward(self, callback):
        name = self.movieObject.getName()
        taskName = "%s_PLAY_BACKWARD" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        group = self.movieObject.getGroup()
        with TaskManager.createTaskChain(Name=taskName, Group=group) as tc:
            with tc.addParallelTask(2) as (tc_chip, tc_sound):
                tc_chip.addTask("TaskMovieReverse", MovieName=name, Reverse=True)
                tc_chip.addTask("TaskMoviePlay", MovieName=name)
                # tc_chip.addTask("TaskMovieLastFrame", MovieName = name, Value = True)
                tc_chip.addTask("TaskFunction", Fn=callback)

                tc_sound.addTask("TaskMoviePlay", MovieName=self.soundMovieName)
            pass
        pass

    def isEndMoving(self, slot):
        # print "-------"
        # print self
        # print slot,self.slotFrom ,self.currentIndex , self.lastIndex - 1,self.slotTo
        if slot == self.slotFrom and self.currentIndex == 0:
            # print "First"
            return True
            pass
        elif slot == self.slotTo and self.currentIndex >= self.lastIndex - 1:
            # print "Last"
            return True
            pass
        else:
            # print "False"
            return False
            pass
        pass

    def detach(self, chip):
        node = chip.getMovieNode()
        self.movieSlot.removeChild(node.node)
        pass

    def attach(self, chip):
        self.movieSlot.removeChildren()
        node = chip.getMovieNode()
        self.movieSlot.addChild(node.node)
        pass

    def getAngle(self):
        return None
        pass

    def getNearestSlot(self):
        deltaSecond = abs(self.lastIndex - self.currentIndex)
        if self.currentIndex < deltaSecond:
            return self.slotFrom
            pass

        return self.slotTo
        pass

    def getMovieData(self):
        resourceMovieName = self.movie.ResourceMovie
        nullObjectsData = Mengine.getNullObjectsFromResourceMovie(resourceMovieName)
        self.movieData = nullObjectsData["move"]
        pass

    def setFrame(self, index):
        # print "setFrame",index,self.lastIndex
        if index < 0:
            index = 0
            pass

        if index > self.lastIndex:
            index = self.lastIndex
            pass

        self.currentIndex = index
        point = self.movieData[index]
        # print "SETFRAME",self
        # print "point",point
        self.movie.setTiming(point["time"])
        # self.movie.movie.update(0)
        pass

    def getNearestIndex(self, position):
        minIndex = -1
        minDelta = 10000

        for index, frame in enumerate(self.movieData):
            delta = Mengine.sqrtf((frame["position"].x - position.x) ** 2 + (frame["position"].y - position.y) ** 2)
            # print "delta ",delta,"index,",index
            if delta < minDelta:
                minDelta = delta
                minIndex = index
                pass
            pass

        # print "SET   position",position,minIndex
        return (minDelta, minIndex)
        pass
