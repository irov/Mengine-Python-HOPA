from Foundation.DefaultManager import DefaultManager
from Foundation.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager

class HogPenalty(BaseEntity):
    def __init__(self):
        super(HogPenalty, self).__init__()
        self.ClickObserver = None
        self.MouseMove = None
        self.tc_penalty = None
        self.clicks = 0
        self.penalty = 10
        self.LegitTime = None
        self.timming = []
        self.MovieEntity = None
        self.penaltyActive = False
        self.penaltySocketBlock = None

        pass

    def _onActivate(self):
        super(HogPenalty, self)._onActivate()
        self.__cleanUp()
        self.UpdateDiffcultyParams()
        self.prepareMovie()
        self.ClickObserver = Notification.addObserver(Notificator.onMouseButtonEvent, self.__clickWatcher)

        pass

    def _onDeactivate(self):
        super(HogPenalty, self)._onDeactivate()
        self.__cleanUp()

    def _onFinalize(self):
        super(HogPenalty, self)._onFinalize()

        self.__cleanUp()

    def __cleanUp(self):
        if self.ClickObserver is not None:
            Notification.removeObserver(self.ClickObserver)
            self.ClickObserver = None

        if self.MouseMove is not None:
            Notification.removeObserver(self.MouseMove)
            self.MouseMove = None

        self.__cancelPenalty()

        if self.MovieEntity is not None:
            self.MovieEntity.removeFromParent()
            self.MovieEntity = None
        self.timming = []

    def prepareMovie(self):
        Movie = self.object.getObject("Movie_Penalty")
        Movie.setEnable(False)

    def __clickWatcher(self, event):
        if event.isDown is True:
            return False

        if self.MouseMove is None:
            self.MouseMove = Notification.addObserver(Notificator.onMouseMove, self.updatePosition)

        clicks = len(self.timming)
        if clicks < 10:
            time = Mengine.getTime()

            self.timming.append(time)
            return False

        presentTime = self.timming[-1]
        pastTime = self.timming[-10]

        if presentTime - pastTime <= self.LegitTime:
            self.__cancelPenalty()

            if self.object.hasObject("Socket_Block"):
                SocketBlock = self.object.getObject("Socket_Block")
                SocketBlock.setInteractive(True)
                SocketBlock.setBlock(True)
            else:
                SocketBlock = None
                pass
            self.timming = []
            Movie = self.object.getObject("Movie_Penalty")
            MovieEn = Movie.getEntity()
            scene = SceneManager.getCurrentScene()
            mainLayer = scene.getSlot("HogUpEffect")
            mainLayer.addChild(MovieEn)
            self.MovieEntity = MovieEn
            arrow_node = Mengine.getArrowNode()
            MainLayer = self.getParent()
            centre = MainLayer.getSize()
            origin = (centre[0] / 2, centre[1] / 2)
            arrowPosition = arrow_node.getLocalPosition()

            arrow_node.disable()
            MovieEn.setOrigin(origin)
            Movie.setPosition(arrowPosition)

            # the arrow and the block are restored by __restorePenalty, also when the chain is cancelled
            self.penaltyActive = True
            self.penaltySocketBlock = SocketBlock

            chain = TaskManager.createTaskChain()
            self.tc_penalty = chain
            with chain as tc:
                tc.addEnable(Movie)
                tc.addTask("TaskMoviePlay", Movie=Movie)
                tc.addFunction(self.__onPenaltyEnd)
            #            Movie.setPlay(True)
            Notification.removeObserver(self.MouseMove)
            self.MouseMove = None

            pass
        time = Mengine.getTime()
        self.timming.append(time)

        return False
        pass

    def updatePosition(self, *params):
        arrow_node = Mengine.getArrowNode()
        new_position = arrow_node.getLocalPosition()
        Movie = self.object.getObject("Movie_Penalty")
        Movie.setPosition(new_position)
        return False
        pass

    def __onPenaltyEnd(self):
        self.tc_penalty = None
        self.__restorePenalty()

    def __cancelPenalty(self):
        chain = self.tc_penalty
        self.tc_penalty = None
        if chain is not None:
            chain.cancel()

        self.__restorePenalty()

    def __restorePenalty(self):
        if self.penaltyActive is False:
            return

        self.penaltyActive = False

        SocketBlock = self.penaltySocketBlock
        self.penaltySocketBlock = None

        arrow_node = Mengine.getArrowNode()
        arrow_node.enable()

        if self.object is not None and self.object.hasObject("Movie_Penalty") is True:
            Movie = self.object.getObject("Movie_Penalty")
            Movie.setEnable(False)

        self.unblock(SocketBlock)

    def unblock(self, Socket):
        self.tc_penalty = None
        if Socket:
            Socket.setBlock(False)
            Socket.setInteractive(False)
            pass
        pass

    def UpdateDiffcultyParams(self):
        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        TypeTime = "HogPenaltyTime%s" % (Difficulty)
        self.LegitTime = DefaultManager.getDefaultFloat(TypeTime, 3)
        self.LegitTime *= 1000  # speed fix
        pass
