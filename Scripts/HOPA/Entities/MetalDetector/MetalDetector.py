from Foundation.Entity.BaseEntity import BaseEntity
from HOPA.ItemManager import ItemManager
from HOPA.CursorManager import CursorManager
from HOPA.MetalDetectorManager import MetalDetectorManager
from Notification import Notification


class MetalDetector(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "DetectPoint")
        pass

    def __init__(self):
        super(MetalDetector, self).__init__()
        self.CurrentMovie = None
        self.MouseMove = None
        pass

    def _onActivate(self):
        super(MetalDetector, self)._onActivate()
        DemonName = self.object.getName()
        self.ItemName = MetalDetectorManager.getItemName(DemonName)
        self.Radius = MetalDetectorManager.getRadius(DemonName)
        self.Range = MetalDetectorManager.getRange(DemonName)
        self.InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        self.Attach = Notification.addObserver(Notificator.onArrowAttach, self.attachFilter)
        self.DeAttach = Notification.addObserver(Notificator.onArrowDeattach, self.deattach)
        self.preparation()
        pass

    def preparation(self):
        self.MovieHot = self.object.getObject("Movie_Hot")
        self.MovieCold = self.object.getObject("Movie_Cold")
        self.MovieHot.setEnable(False)
        self.MovieCold.setEnable(False)
        self.position = self.object.getParam("DetectPoint")

        MainLayer = self.object.getParent()
        centre = MainLayer.getSize()
        origin = (centre[0] / 2, centre[1] / 2)
        self.MovieHot.getEntity().setOrigin(origin)
        self.MovieCold.getEntity().setOrigin(origin)
        pass

    def _onDeactivate(self):
        super(MetalDetector, self)._onDeactivate()

        MovieCouldEn = self.MovieCold.getEntity()
        MovieCouldEn.removeFromParent()
        MovieHotEntity = self.MovieHot.getEntity()
        MovieHotEntity.removeFromParent()

        Notification.removeObserver(self.Attach)
        Notification.removeObserver(self.DeAttach)
        CursorManager.setBlockCursorUpdate(block=False)
        if self.MouseMove:
            Notification.removeObserver(self.MouseMove)
            pass
        pass

    def attachFilter(self, atach):
        if self.InventoryItem is atach:
            self.__setParams()
            self.InventoryItem.setEnable(False)
            CursorManager.setBlockCursorUpdate(block=True)
            pass
        return False
        pass

    def deattach(self, atach):
        if self.InventoryItem is not atach:
            return False
            pass
        self.CurrentMovie.setPlay(False)
        self.CurrentMovie.setEnable(False)
        Notification.removeObserver(self.MouseMove)
        CursorManager.setBlockCursorUpdate(block=False)
        cursorChildren = CursorManager.getCursorChildren()
        if len(cursorChildren) == 0:
            return

        currentCursor = cursorChildren[0]
        currentCursor.setEnable(True)
        CursorManager.setCursorMode("Default")

        self.MouseMove = None
        return False
        pass

    def __setParams(self):
        self.CurrentMovie = self.MovieCold
        self.MouseMove = Notification.addObserver(Notificator.onMouseMove, self.updateSpeedTiming)
        return True
        pass

    def updateSpeedTiming(self, *params):
        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()

        arrowPosition = arrow_node.getLocalPosition()

        distanse = (((arrowPosition[0] - self.position[0]) ** 2 + (arrowPosition[1] - self.position[1]) ** 2)) ** .5
        gaus = ((arrowPosition[0] - self.position[0]), (arrowPosition[1] - self.position[1]))
        if distanse < self.Radius:
            self.changeMovieTo(self.MovieHot)
        else:
            self.changeMovieTo(self.MovieCold)

        Movie = self.CurrentMovie
        MovieEn = Movie.getEntity()

        arrow_node.addChild(MovieEn)

        cursorChildren = CursorManager.getCursorChildren()
        if len(cursorChildren) == 0:
            return

        currentCursor = cursorChildren[0]
        currentCursor.setEnable(False)

        #        speeedFactor = self.Range/(distanse+10)
        speeedFactor = 1 + (self.Radius / (distanse + 10)) ** 2
        if speeedFactor > 7:
            speeedFactor = 7

        Movie.setSpeedFactor(speeedFactor)
        return False
        pass

    def changeMovieTo(self, Movie):
        if Movie is self.MovieCold:
            self.CurrentMovie = self.MovieCold
            self.MovieHot.setPlay(False)
            self.MovieHot.setEnable(False)
            self.CurrentMovie.setEnable(True)
            self.CurrentMovie.setPlay(True)
        else:
            self.CurrentMovie = self.MovieHot
            self.MovieCold.setPlay(False)
            self.MovieCold.setEnable(False)
            self.CurrentMovie.setEnable(True)
            self.CurrentMovie.setPlay(True)
        pass
