from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Functor import Functor

MOV_TRANSPORTER = "Movie2_Transporter"
MOV_TRANSPORTER_REV = "Movie2_Transporter_Reverse"
MOV_TRANSPORTER_SOUND = "Movie2_Sound_Transporter"
SOCKET_TRANSPORTER = "Socket_Transporter"
SLOT_MOVE = "move"

class PathChipsTransporter(BaseEntity):
    def __init__(self):
        super(PathChipsTransporter, self).__init__()
        self.attachNode = None

        self.movie = None
        self.movieReverse = None
        self.socket = None
        self.observerFn = None

        self.reversed = False

        self.block = False
        pass

    def setBlock(self, state):
        self.block = state
        pass

    #    def getMovieData(self):
    #        resourceMovieName = self.movie.getResourceMovie()
    #        nullObjectsData = Mengine.getNullObjectsFromResourceMovie(resourceMovieName)
    #        movieData = nullObjectsData["move"]
    #        self.lastTiming = movieData[len(movieData) - 1]["time"]
    #        self.firstTiming = movieData[0]["time"]
    #        pass

    def _onInitialize(self, *args, **kwargs):
        super(PathChipsTransporter, self)._onInitialize(*args, **kwargs)
        self.attachNode = Mengine.createNode("Interender")

        # self.socket = self.object.getObject(SOCKET_TRANSPORTER)
        # self.socket.setInteractive(True)
        pass

    def _onActivate(self):
        super(PathChipsTransporter, self)._onActivate()
        self.movie = self.object.getObject(MOV_TRANSPORTER)
        self.movieReverse = self.object.getObject(MOV_TRANSPORTER_REV)

        self.attachToForwardMovie()

        self.socket = self.object.getObject(SOCKET_TRANSPORTER)
        self.socket.setInteractive(True)
        pass

    def _onDeactivate(self):
        super(PathChipsTransporter, self)._onDeactivate()
        if TaskManager.existTaskChain("TRANSPORTER_FORWARD") is True:
            TaskManager.cancelTaskChain("TRANSPORTER_FORWARD")
            pass

        if TaskManager.existTaskChain("TRANSPORTER_BACKWARD") is True:
            TaskManager.cancelTaskChain("TRANSPORTER_BACKWARD")
            pass

        self.socket.setInteractive(False)
        # self.movieSlot.removeAllChild()
        pass

    def _onFinalize(self):
        super(PathChipsTransporter, self)._onFinalize()

        if self.observerFn != None:
            Notification.removeObserver(self.observerFn)
            pass

        if self.attachNode is not None:
            Mengine.destroyNode(self.attachNode)
            self.attachNode = None
            pass
        pass

    def addClickObserver(self, callback):
        if self.observerFn != None:
            Notification.removeObserver(self.observerFn)
            pass
        self.observerFn = Notification.addObserver(Notificator.onSocketClick,
                                                   Functor(self.__onSocketClick, self.socket, callback))
        pass

    def __onSocketClick(self, socket, wait, callback):
        if self.block is True:
            return False
            pass

        if socket != wait:
            # print socket,wait
            return False
            pass

        callback()
        return False
        pass

    #
    #    def getMovieSlotAngle(self):
    #        angle =  self.movieSlot.getAngle()
    #        return angle
    #        pass

    def attachToForwardMovie(self):
        self.movie.setEnable(True)
        self.movieReverse.setEnable(False)

        movieForwardEntity = self.movie.getEntity()
        self.movie.setLastFrame(False)

        movieSlotForward = movieForwardEntity.getMovieSlot(SLOT_MOVE)

        self.attachNode.removeFromParent()

        movieSlotForward.addChild(self.attachNode)
        pass

    def attachToBackwardMovie(self):
        self.movie.setEnable(False)
        self.movieReverse.setEnable(True)

        movieBackwardEntity = self.movieReverse.getEntity()
        self.movieReverse.setLastFrame(False)

        movieSlotBackward = movieBackwardEntity.getMovieSlot(SLOT_MOVE)

        self.attachNode.removeFromParent()

        movieSlotBackward.addChild(self.attachNode)
        pass

    def playForward(self, callback):
        if TaskManager.existTaskChain("TRANSPORTER_FORWARD") is True:
            TaskManager.cancelTaskChain("TRANSPORTER_FORWARD")
            pass

        self.attachToForwardMovie()

        with TaskManager.createTaskChain(Name="TRANSPORTER_FORWARD", Group=self.object) as tc:
            with tc.addParallelTask(2) as (tc_transporter, tc_sound):
                # tc_transporter.addTask("TaskMovieReverse", MovieName = "Movie_Transporter", Reverse = False)
                tc_transporter.addTask("TaskMovie2Play", Movie2=self.movie)
                # tc_transporter.addTask("TaskMovieLastFrame", MovieName = "Movie_Transporter", Value = True)

                tc_sound.addTask("TaskMovie2Play", Movie2Name=MOV_TRANSPORTER_SOUND)
            pass
            tc.addFunction(callback)
        pass

    def playBackward(self, callback):
        if TaskManager.existTaskChain("TRANSPORTER_BACKWARD") is True:
            TaskManager.cancelTaskChain("TRANSPORTER_BACKWARD")
            pass

        self.attachToBackwardMovie()

        with TaskManager.createTaskChain(Name="TRANSPORTER_BACKWARD", Group=self.object) as tc:
            with tc.addParallelTask(2) as (tc_transporter, tc_sound):
                # tc_transporter.addTask("TaskMovieReverse", MovieName = "Movie_Transporter", Reverse = True)
                tc_transporter.addTask("TaskMovie2Play", Movie2=self.movieReverse)

                # tc_transporter.addTask("TaskMovieLastFrame", MovieName = "Movie_Transporter", Value = True)
                tc_sound.addTask("TaskMovie2Play", Movie2Name=MOV_TRANSPORTER_SOUND)
            tc.addFunction(callback)
            pass
        pass

    def detachFromMovie(self, node):
        node.removeFromParent()
        pass

    def attachToMovie(self, node):
        # self.movieSlot.removeAllChild()
        # self.movieSlot.addChild(node.node)

        self.attachNode.removeChildren()
        self.attachNode.addChild(node.node)
        pass

    pass
