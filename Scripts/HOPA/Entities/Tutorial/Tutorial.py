from Foundation.Entity.BaseEntity import BaseEntity
from HOPA.TutorialManager import TutorialManager
from Notification import Notification


class Tutorial(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "Polygon")
        pass

    def __init__(self):
        super(Tutorial, self).__init__()
        self.ActualTutorial = None
        self.hotspot = None
        self.garbage = []
        self.ShowHandler = None
        self.HideHandler = None

    def _onRestore(self):
        super(Tutorial, self)._onRestore()
        self.Text = self.object.getObject("Text_Sample")

    def _onActivate(self):
        super(Tutorial, self)._onActivate()
        self.restoring()
        self.ShowHandler = Notification.addObserver(Notificator.onTutorialShow, self.onShow)
        self.HideHandler = Notification.addObserver(Notificator.onTutorialHide, self.onHide)

    def restoring(self):
        if self.ActualTutorial is None:
            return
        self.onShow(self.ActualTutorial)

    def onShow(self, Name):
        if self.ActualTutorial is not None:
            self.onHide()
            pass
        movieName = TutorialManager.getMovieName(Name)
        textId = TutorialManager.getText(Name)
        movie = self.object.getObject(movieName)
        movie.setEnable(True)
        self.movieBound(movie, textId)
        movie.setPlay(True)
        self.ActualTutorial = Name

        return False

    def onHide(self):
        if self.ActualTutorial is None:
            return False

        pastMovieName = TutorialManager.getMovieName(self.ActualTutorial)
        pastMovie = self.object.getObject(pastMovieName)
        self.movieUnbound()
        pastMovie.setEnable(False)
        self.Text.setEnable(False)
        self.ActualTutorial = None
        return False

    def movieBound(self, movieObject, textId):
        movieEn = movieObject.getEntity()
        SlotInstance = movieEn.getMovieSlot("hotspot")
        self.hotspot = Mengine.createNode("HotSpotPolygon")
        self.hotspot.setPolygon(self.Polygon)
        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        SlotInstance.addChild(self.hotspot)
        self.hotspot.enableGlobalMouseEvent(True)
        self.garbage.append(self.hotspot)
        # ------> text
        TextEn = self.Text.getEntity()
        self.Text.setEnable(True)
        SlotInstance.addChild(TextEn)

        self.Text.setParam("TextID", textId)
        self.garbage.append(TextEn)

    def movieUnbound(self):
        self.cleanGarbage()
        if self.hotspot is not None:
            self.hotspot.enableGlobalMouseEvent(False)
            self.hotspot.setEventListener(onHandleMouseButtonEvent=None)
            Mengine.destroyNode(self.hotspot)
            self.hotspot = None

    def _onDeactivate(self):
        super(Tutorial, self)._onDeactivate()
        self.movieUnbound()
        Notification.removeObserver(self.ShowHandler)
        Notification.removeObserver(self.HideHandler)

    def cleanGarbage(self):
        for garbEn in self.garbage:
            garbEn.removeFromParent()
        self.garbage = []

    def _onMouseButtonEvent(self, touchId, x, y, button, isDown, isPressed):
        if isDown is True:
            self.onHide()
            return True

        return False

    def getMovieObject(self, Name):
        movieName = TutorialManager.getMovieName(Name)
        movie = self.object.getObject(movieName)

        return movie
