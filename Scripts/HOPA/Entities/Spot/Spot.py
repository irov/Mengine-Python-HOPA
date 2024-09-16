from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Notification import Notification


class Spot(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "FadeColor")
        pass

    def __init__(self):
        super(Spot, self).__init__()
        self.hotspots = []
        self.sprites = []
        self.__attached = False
        pass

    def _onActivate(self):
        super(Spot, self)._onActivate()

        self.movie_Spot = self.object.getObject("Movie_Spot").getEntity()
        movie = self.movie_Spot.getAnimatable()
        self.movieSize = movie.getSize()
        #        self.movieSize = (450,413)
        resolution = Mengine.getContentResolution()
        width = resolution.getWidth()
        height = resolution.getHeight()

        whitePixelRes = Mengine.getResourceReference("WhitePixel")

        self.setOrigin((self.movieSize[0] * 0.5, self.movieSize[1] * 0.5))
        # left
        fadeSpriteLeft = Mengine.createSprite("fadeSpriteLeft", whitePixelRes)
        size_x = width
        size_y = height * 2 + self.movieSize[1]
        x = -(size_x)
        y = -(size_y * 0.5)
        fadeSpriteLeft.setCustomSize((size_x, size_y))
        fadeSpriteLeft.setLocalPosition((x, y))
        fadeSpriteLeft.setLocalColor(self.FadeColor)
        fadeSpriteLeft.setResourceImage(whitePixelRes)
        self.addChild(fadeSpriteLeft)
        self.sprites.append(fadeSpriteLeft)

        fadeHSLeft = Mengine.createNode("HotSpotPolygon")
        p1 = (0, 0)
        p2 = (size_x, 0)
        p3 = (size_x, size_y)
        p4 = (0, size_y)
        polygon = [p1, p2, p3, p4]
        fadeHSLeft.setPolygon(polygon)
        fadeHSLeft.setLocalPosition((x, y))
        fadeHSLeft.enable()
        self.addChild(fadeHSLeft)
        self.hotspots.append(fadeHSLeft)
        fadeHSLeft.setEventListener(onHandleMouseButtonEvent=self._onHSClick)

        # top
        fadeSpriteTop = Mengine.createSprite("fadeSpriteTop", whitePixelRes)
        size_x = self.movieSize[0]
        size_y = height
        x = 0
        y = -size_y
        fadeSpriteTop.setCustomSize((size_x, size_y))
        fadeSpriteTop.setLocalPosition((x, y))
        fadeSpriteTop.setLocalColor(self.FadeColor)
        fadeSpriteTop.setResourceImage(whitePixelRes)
        self.addChild(fadeSpriteTop)
        self.sprites.append(fadeSpriteTop)

        fadeHSTop = Mengine.createNode("HotSpotPolygon")
        p1 = (0, 0)
        p2 = (size_x, 0)
        p3 = (size_x, size_y)
        p4 = (0, size_y)
        polygon = [p1, p2, p3, p4]
        fadeHSTop.setPolygon(polygon)
        fadeHSTop.setLocalPosition((x, y))
        fadeHSTop.enable()
        self.addChild(fadeHSTop)
        self.hotspots.append(fadeHSTop)
        fadeHSTop.setEventListener(onHandleMouseButtonEvent=self._onHSClick)

        # right
        fadeSpriteRight = Mengine.createSprite("fadeSpriteRight", whitePixelRes)
        size_x = width
        size_y = height * 2 + self.movieSize[1]
        x = self.movieSize[0]
        y = -(size_y * 0.5)
        fadeSpriteRight.setCustomSize((size_x, size_y))
        fadeSpriteRight.setLocalPosition((x, y))
        fadeSpriteRight.setLocalColor(self.FadeColor)
        fadeSpriteRight.setResourceImage(whitePixelRes)
        self.addChild(fadeSpriteRight)
        self.sprites.append(fadeSpriteRight)

        fadeHSRight = Mengine.createNode("HotSpotPolygon")
        p1 = (0, 0)
        p2 = (size_x, 0)
        p3 = (size_x, size_y)
        p4 = (0, size_y)
        polygon = [p1, p2, p3, p4]
        fadeHSRight.setPolygon(polygon)
        fadeHSRight.setLocalPosition((x, y))
        fadeHSRight.enable()
        self.addChild(fadeHSRight)
        self.hotspots.append(fadeHSRight)
        fadeHSRight.setEventListener(onHandleMouseButtonEvent=self._onHSClick)

        # bottom
        fadeSpriteBottom = Mengine.createSprite("fadeSpriteBottom", whitePixelRes)
        size_x = self.movieSize[0]
        size_y = height
        x = 0
        y = self.movieSize[1]
        fadeSpriteBottom.setCustomSize((size_x, size_y))
        fadeSpriteBottom.setLocalPosition((x, y))
        fadeSpriteBottom.setLocalColor(self.FadeColor)
        fadeSpriteBottom.setResourceImage(whitePixelRes)
        self.addChild(fadeSpriteBottom)
        self.sprites.append(fadeSpriteBottom)

        fadeHSBottom = Mengine.createNode("HotSpotPolygon")
        p1 = (0, 0)
        p2 = (size_x, 0)
        p3 = (size_x, size_y)
        p4 = (0, size_y)
        polygon = [p1, p2, p3, p4]
        fadeHSBottom.setPolygon(polygon)
        fadeHSBottom.setLocalPosition((x, y))
        fadeHSBottom.enable()
        self.addChild(fadeHSBottom)
        self.hotspots.append(fadeHSBottom)
        fadeHSBottom.setEventListener(onHandleMouseButtonEvent=self._onHSClick)

        DragAndDropHS = Mengine.createNode("HotSpotPolygon")
        p1 = (0, 0)
        p2 = (self.movieSize[0], 0)
        p3 = self.movieSize
        p4 = (0, self.movieSize[1])
        polygon = [p1, p2, p3, p4]
        DragAndDropHS.setPolygon(polygon)
        DragAndDropHS.setLocalPosition((0, 0))
        DragAndDropHS.enable()
        DragAndDropHS.setDefaultHandle(False)
        self.addChild(DragAndDropHS)
        self.hotspots.append(DragAndDropHS)
        DragAndDropHS.setEventListener(onHandleMouseButtonEvent=self._onHSMainClick)

        offsetX = 0
        offsetY = 0

        if DemonManager.hasDemon("HOGViewport") is True:
            HOGViewport = DemonManager.getDemon("HOGViewport")
            sizeViewport = HOGViewport.getSize()
            offsetX = sizeViewport[0][0]
            offsetY = sizeViewport[0][1]

            width = sizeViewport[1][0] - offsetX
            height = sizeViewport[1][1] - offsetY
            pass

        centerPos = (width * 0.5 + offsetX, height * 0.5 + offsetY)

        self.translate(centerPos)

        self.onSpotHideObserver = Notification.addObserver(Notificator.onSpotHide, self.__onSpotHide)
        Notification.notify(Notificator.onSpotActivate, self.object)
        pass

    def __onSpotHide(self, hideTime, fadeTime):
        if TaskManager.existTaskChain("SpotHideDelay") is True:
            return False
            pass

        for hs in self.hotspots:
            hs.disable()
            pass

        with TaskManager.createTaskChain(Name="SpotHideDelay") as tc:
            with tc.addParallelTask(2) as (tc_1, tc_2):
                with tc_1.addParallelTask(len(self.sprites)) as tc_hides:
                    for tc_hide, sprite in zip(tc_hides, self.sprites):
                        tc_hide.addTask("TaskNodeAlphaTo", Node=sprite, To=0.0, Time=fadeTime)
                        pass

                tc_2.addTask("TaskNodeAlphaTo", Node=self.movie_Spot, To=0.0, Time=fadeTime)
                pass

            tc.addTask("TaskDelay", Time=hideTime)
            tc.addTask("TaskFunction", Fn=self.__onSpotShow, Args=(fadeTime,))
            pass

        return False
        pass

    def __onSpotShow(self, fadeTime):
        for hs in self.hotspots:
            hs.enable()
            pass

        with TaskManager.createTaskChain(Name="SpotHideShow") as tc:
            with tc.addParallelTask(2) as (tc_1, tc_2):
                with tc_1.addParallelTask(len(self.sprites)) as tc_hides:
                    for tc_hide, sprite in zip(tc_hides, self.sprites):
                        tc_hide.addTask("TaskNodeAlphaTo", Node=sprite, To=self.FadeColor[3], Time=fadeTime)
                        pass

                tc_2.addTask("TaskNodeAlphaTo", Node=self.movie_Spot, To=1.0, Time=fadeTime)
                pass
            pass

        self.movie_Spot.enable()
        pass

    def _onDeactivate(self):
        super(Spot, self)._onDeactivate()
        if TaskManager.existTaskChain("SpotHideDelay") is True:
            TaskManager.cancelTaskChain("SpotHideDelay")
            pass
        if TaskManager.existTaskChain("SpotHideShow") is True:
            TaskManager.cancelTaskChain("SpotHideShow")
            pass

        for node in self.hotspots + self.sprites:
            node.removeFromParent()
            Mengine.destroyNode(node)
            pass

        self.hotspots = []
        self.sprites = []

        self.translate((0, 0))
        self.setOrigin((0, 0))
        self.setLocalPosition((0, 0))
        self.removeRelationTransformation()

        Notification.removeObserver(self.onSpotHideObserver)
        Notification.notify(Notificator.onSpotDeactivate, self.object)
        pass

    def _onHSClick(self, touchId, x, y, button, isDown, isPressed):
        # No multitouch here
        if touchId != 0:
            return False

        if isDown is True:
            self.__arrowAttach()
            return True
            pass

        return False
        pass

    def _onHSMainClick(self, touchId, x, y, button, isDown, isPressed):
        # No multitouch here
        if touchId != 0:
            return False

        if isDown is True:
            self.__arrowAttach()
            return False
            pass

        self.__arrowDetach()
        return False
        pass

    def __arrowAttach(self):
        self.__attached = True

        self.translate((0, 0))
        self.setLocalPosition((0, 0))

        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        self.setRelationTransformation(arrow_node)
        pass

    def __arrowDetach(self):
        if not self.__attached:
            return

        self.__attached = False

        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        tempPos = arrow_node.getWorldPosition()

        self.removeRelationTransformation()
        self.translate(tempPos)
        pass

    pass
