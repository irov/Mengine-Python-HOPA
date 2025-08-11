from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager

class HogPenalty(BaseEntity):
    def __init__(self):
        super(HogPenalty, self).__init__()
        self.ClickObserver = None
        self.clicks = 0
        self.penalty = 10
        self.LegitTime = None
        self.timming = []
        self.MovieEntity = None

        pass

    def _onActivate(self):
        super(HogPenalty, self)._onActivate()
        self.UpdateDiffcultyParams()
        self.prepareMovie()
        self.ClickObserver = Notification.addObserver(Notificator.onMouseButtonEvent, self.__clickWatcher)

        pass

    def _onDeactivate(self):
        super(HogPenalty, self)._onDeactivate()
        Notification.removeObserver(self.ClickObserver)
        if self.MovieEntity:
            self.MovieEntity.removeFromParent()

    def prepareMovie(self):
        Movie = self.object.getObject("Movie_Penalty")
        Movie.setEnable(False)

    def __clickWatcher(self, event):
        if event.isDown is True:
            return False

        self.MouseMove = Notification.addObserver(Notificator.onMouseMove, self.updatePosition)

        clicks = len(self.timming)
        if clicks < 10:
            time = Mengine.getTime()

            self.timming.append(time)
            return False

        presentTime = self.timming[-1]
        pastTime = self.timming[-10]

        if presentTime - pastTime <= self.LegitTime:
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
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            MainLayer = self.getParent()
            centre = MainLayer.getSize()
            origin = (centre[0] / 2, centre[1] / 2)
            arrowPosition = arrow_node.getLocalPosition()

            arrow_node.disable()
            MovieEn.setOrigin(origin)
            Movie.setPosition(arrowPosition)

            with TaskManager.createTaskChain() as tc:
                tc.addEnable(Movie)
                tc.addTask("TaskMoviePlay", Movie=Movie)
                tc.addFunction(arrow_node.enable)
                tc.addDisable(Movie)
                tc.addFunction(self.unblock, SocketBlock)
            #            Movie.setPlay(True)
            Notification.removeObserver(self.MouseMove)

            pass
        time = Mengine.getTime()
        self.timming.append(time)

        return False
        pass

    def updatePosition(self, *params):
        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        new_position = arrow_node.getLocalPosition()
        Movie = self.object.getObject("Movie_Penalty")
        Movie.setPosition(new_position)
        return False
        pass

    def unblock(self, Socket):
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
