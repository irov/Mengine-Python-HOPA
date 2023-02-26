from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity

class StaticPopUp(BaseEntity):
    def __init__(self):
        super(StaticPopUp, self).__init__()
        self.text = None
        self.textID = None
        self.Movie_Frame = None
        self.FramesNode = None
        self.textEn = None
        self.TextMessageCS = "TextMessage"
        pass

    def _onInitialize(self, obj):
        super(StaticPopUp, self)._onInitialize(obj)
        pass

    def _onActivate(self):
        self.text = self.object.getObject("Text_Message")
        if self.object.hasObject("Movie_Frame"):
            self.Movie_Frame = self.object.getObject("Movie_Frame")
            pass
        self.text.setPosition((0, 0))
        if self.Movie_Frame is not None:
            self.Movie_Frame.setEnable(False)
            self.textEn = self.text.getEntity()
        self.text.setEnable(False)
        pass

    def _onRestore(self):
        pass

    def _onDeactivate(self):
        self.textID = None
        self.clean_up()
        self.text.setEnable(False)
        self.Movie_Frame.setEnable(False)

        pass

    def show(self, textID, CustomMovie=None):
        if self.Movie_Frame is None and textID:  # nothing to do
            return
            pass
        self.textID = textID
        self._onCompleteShow(True)

    def _onCompleteShow(self, isSkip):
        self.text.setParam("TextID", self.textID)
        self.Movie_Frame.setEnable(True)
        MovieFrameEntity = self.Movie_Frame.getEntity()
        currentTextPosition = self._getTextPosition()
        self.text.setEnable(True)
        self.Movie_Frame.setEnable(True)
        self.FramesNode = MovieFrameEntity.getMovieSlot(self.TextMessageCS)
        self.FramesNode.addChild(self.textEn)
        MovieFrameEntity.setWorldPosition(currentTextPosition)
        self.setEventListener(onGlobalHandleMouseMove=self._onGlobalHandleMouseMove)
        self.enableGlobalMouseEvent(True)
        pass

    def _getTextPosition(self):  # need refactoring
        arrowScreenPosition = Mengine.getCursorPosition()
        if self.FramesNode is None:
            return arrowScreenPosition
            pass
        textLength = self.textEn.getLength()
        text_X = textLength.x
        StaticPopUpIndentArrowX = DefaultManager.getDefaultFloat("StaticPopUpIndentArrowX", 30)
        StaticPopUpIndentArrowY = DefaultManager.getDefaultFloat("StaticPopUpIndentArrowY", 30)

        ContentResolution = Mengine.getContentResolution()
        ContentResolutionWidth = ContentResolution.getWidth()
        ContentResolutionHeight = ContentResolution.getHeight()
        currentPosition = None

        XExpression = arrowScreenPosition.x + 3 * text_X + StaticPopUpIndentArrowX
        YExpression = arrowScreenPosition.y + 2 * text_X + StaticPopUpIndentArrowY

        if XExpression > ContentResolutionWidth:
            currentPosition = (ContentResolutionWidth - 3 * text_X - StaticPopUpIndentArrowX, arrowScreenPosition.y + StaticPopUpIndentArrowY)
            pass
        elif YExpression > ContentResolutionHeight:
            newYPosition = ContentResolutionHeight - 2 * text_X + StaticPopUpIndentArrowY
            if currentPosition is not None:
                currentPosition = (currentPosition[0], newYPosition)
                pass
            else:
                currentPosition = (arrowScreenPosition.x + StaticPopUpIndentArrowX, newYPosition)
                pass
        else:
            currentPosition = (arrowScreenPosition.x + StaticPopUpIndentArrowX, arrowScreenPosition.y + StaticPopUpIndentArrowY)
            pass

        return currentPosition

    def _onGlobalHandleMouseMove(self, en, touchId, x, y, dx, dy):
        if self.textID is None:
            return
            pass
        currentTextPosition = self._getTextPosition()
        self.Movie_Frame.setPosition(currentTextPosition)
        return
        pass

    def hide(self):
        self.clean_up()
        self.text.setEnable(False)
        self.Movie_Frame.setEnable(False)
        self.textID = None
        return False
        pass

    def clean_up(self):
        if self.FramesNode is None:
            return
            pass
        self.text.setEnable(False)
        self.FramesNode.removeChild(self.textEn)
        self.FramesNode = None
        self.enableGlobalMouseEvent(False)
        pass