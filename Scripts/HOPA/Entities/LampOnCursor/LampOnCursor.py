from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from HOPA.LampOnCursorManager import LampOnCursorManager

class LampOnCursor(BaseEntity):
    def __init__(self):
        super(LampOnCursor, self).__init__()
        self.MousePositionProviderID = None
        self.MovieShadow = None
        self.MovieLamp = None

        self.MouseMoveHandlerID = None

    def _onPreparation(self):
        super(LampOnCursor, self)._onPreparation()
        self.MovieShadow = self.object.getObject("Movie2_Shadow")
        self.MovieShadow.setEnable(False)

        self.MovieLamp = self.object.getObject("Movie2_Lamp_Idle")
        self.MovieLamp.setEnable(False)

    def _onActivate(self):
        super(LampOnCursor, self)._onActivate()

        currentSceneName = SceneManager.getCurrentSceneName()
        if LampOnCursorManager.isLampOnCursorScene(currentSceneName) is False:
            return

        self.MovieShadow.setEnable(True)
        self.MovieLamp.setEnable(True)

        cursorPosition = Mengine.getCursorPosition()
        self.updateShadowPosition(cursorPosition.x, cursorPosition.y)

        # self.MouseMoveHandlerID = Mengine.addMouseMoveHandler(self.__onMouseMove)
        # Mengine.enableGlobalHandler(self.MouseMoveHandlerID, True)

        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, None, self.__onMousePositionChange)

    def __onMouseMove(self, touchId, x, y, dx, dy):
        # print touchId, x, y, dx, dy
        self.updateShadowPosition(x, y)

    def __onMousePositionChange(self, touchID, position):
        # print touchID, position
        self.updateShadowPosition(position.x, position.y)

    def updateShadowPosition(self, x, y):
        entityNode = self.MovieShadow.getEntityNode()
        entityNode.setWorldPosition((x, y))

        entityNode = self.MovieLamp.getEntityNode()
        entityNode.setWorldPosition((x, y))

    def _onDeactivate(self):
        super(LampOnCursor, self)._onDeactivate()
        self.MovieShadow = None
        self.MovieLamp = None

        if self.MouseMoveHandlerID is not None:
            Mengine.removeGlobalHandler(self.MouseMoveHandlerID)
        self.MouseMoveHandlerID = None

        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
        self.MousePositionProviderID = None