from Foundation.TaskManager import TaskManager


class FragmentsRollMoving(object):
    def __init__(self, movie, soundMovie, movieReverse=None):
        super(FragmentsRollMoving, self).__init__()
        self.movieObjectReverse = movieReverse
        self.movieObject = movie
        self.movie = movie.getEntity()
        self.movieData = {}
        self.getMovieData()
        self.movieSlot = self.movie.getMovieSlot("move")
        self.currentIndex = 0
        self.lastIndex = len(self.movieData) - 2
        self.soundMovie = soundMovie

        self.attachNode = Mengine.createNode("Interender")
        self.movieSlot.addChild(self.attachNode)
        pass

    def finalize(self):
        if self.attachNode is not None:
            Mengine.destroyNode(self.attachNode)
            self.attachNode = None
            pass

        self.movieObject = None
        self.movieObjectReverse = None
        self.movie = None
        self.movieSlot = None
        self.soundMovie = None
        pass

    def isEndMoving(self):
        if self.currentIndex == self.lastIndex:
            return True
            pass

        return False
        pass

    def detach(self, chip):
        node = chip.getNode()
        node.removeFromParent()
        pass

    def attach(self, chip):
        # self.movieSlot.removeAllChild()
        # node = chip.getNode()
        # self.movieSlot.addChild(node)

        self.attachNode.removeChildren()
        node = chip.getNode()
        self.attachNode.addChild(node)
        pass

    def isNearEnd(self):
        half = self.lastIndex / 2
        if self.currentIndex > half:
            return True
            pass
        return False
        pass

    def attachToForwardMovie(self):
        movieForwardEntity = self.movie

        movieSlotForward = movieForwardEntity.getMovieSlot("move")

        self.attachNode.removeFromParent()
        movieSlotForward.addChild(self.attachNode)
        pass

    def attachToBackwardMovie(self):
        movieBackwardEntity = self.movieObjectReverse.getEntity()

        movieSlotBackward = movieBackwardEntity.getMovieSlot("move")

        self.attachNode.removeFromParent()

        movieSlotBackward.addChild(self.attachNode)
        pass

    def moveToEnd(self, callback):
        name = self.movieObject.getName()
        taskName = "%s_PLAY_FORWARD" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        curPoint = self.getPoint(self.currentIndex)
        curTime = curPoint["time"] * 1000  # time param fix for movie2

        self.movieObject.setParam("StartTiming", curTime)

        with TaskManager.createTaskChain(Name=taskName, Group=None) as tc:
            with tc.addParallelTask(2) as (tc_element, tc_sound):
                tc_element.addTask("TaskMovieLastFrame", Movie=self.movieObject, Value=False)
                tc_element.addTask("TaskMovie2Play", Movie2=self.movieObject, StartTiming=curTime)
                tc_element.addFunction(callback)

                tc_sound.addTask("TaskMovie2Play", Movie2=self.soundMovie)
            pass
        pass

    def moveToBegin(self, callback):
        name = self.movieObject.getName()
        taskName = "%s_PLAY_BACKWARD" % (name)
        if TaskManager.existTaskChain(taskName) is True:
            TaskManager.cancelTaskChain(taskName)
            pass

        curPoint = self.getPoint(self.currentIndex)
        movieReverseEntity = self.movieObjectReverse.getEntity()
        duration = movieReverseEntity.getDuration()
        curTime = duration - (curPoint["time"] * 1000)  # time param fix for movie2

        self.attachToBackwardMovie()

        # self.movieObject.setParam("StartTiming",curTime)
        with TaskManager.createTaskChain(Name=taskName, Group=None) as tc:
            with tc.addParallelTask(2) as (tc_element, tc_sound):
                tc_element.addTask("TaskMovieLastFrame", Movie=self.movieObjectReverse, Value=False)
                # tc_element.addTask("TaskMovieReverse", Movie = self.movieObject, Reverse = True)
                tc_element.addTask("TaskMovie2Play", Movie2=self.movieObjectReverse, StartTiming=curTime)
                tc_element.addFunction(self.attachToForwardMovie)
                tc_element.addFunction(callback)

                tc_sound.addTask("TaskMovie2Play", Movie2=self.soundMovie)

            pass
        pass

    def getMovieData(self):
        movie_res = self.movie.ResourceMovie
        movie_comp_name = self.movie.CompositionName
        # null_objects_data = Mengine.getNullObjectsFromResourceMovie(movie_res)    # old method for movie1
        null_objects_data = Mengine.getNullObjectsFromResourceMovie2(movie_res, movie_comp_name)
        self.movieData = null_objects_data["move"]

    def moveForwardOneFrame(self):
        frame = self.currentIndex + 1
        self.setFrame(frame)
        pass

    def moveBackwardOneFrame(self):
        frame = self.currentIndex - 1
        self.setFrame(frame)
        pass

    def setFrame(self, index):
        if index < 0:
            index = 0
            pass

        if index > self.lastIndex:
            index = self.lastIndex
            pass

        self.currentIndex = index
        point = self.getPoint(index)
        self.movie.setTiming(point["time"] * 1000)  # time param fix for movie2
        pass

    def getPoint(self, index):
        return self.movieData[index]
        pass

    pass
