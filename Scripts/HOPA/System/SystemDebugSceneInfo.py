from Foundation.ArrowManager import ArrowManager
from Foundation.SceneManager import SceneManager
from Foundation.Params import Params
from Foundation.System import System
from HOPA.ZoomManager import ZoomManager


SCHEDULE_NOT_ACTIVE = 0


class SystemDebugSceneInfo(System):

    def __init__(self):
        super(SystemDebugSceneInfo, self).__init__()
        self._scheduleId = SCHEDULE_NOT_ACTIVE

    def _onParams(self, params):
        super(SystemDebugSceneInfo, self)._onParams(params)
        self.timingViewTime = params.get("TimingViewTime", 500.0)
        self.textNode = None
        self.enable = False
        self.__text = None

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)

        if _QUALITYASSURANCE is True:
            self.__autoEnableForQA()

        return True

    def __removeSchedule(self):
        if self._scheduleId == SCHEDULE_NOT_ACTIVE:
            return

        if self.textNode is not None and self.enable is False:
            self.__destroyNode()

        self._scheduleId = SCHEDULE_NOT_ACTIVE

        if Mengine.scheduleRemove(self._scheduleId) is False:
            Trace.log("System", 0, "Failed to remove local schedule with id {}".format(self._scheduleId))

    def __attachSchedule(self, reloadTime):
        self.__removeSchedule()
        self._scheduleId = Mengine.schedule(reloadTime, self.__onSchedule)

    def __destroyNode(self):
        if self.textNode is not None:
            self.textNode.removeFromParent()
            Mengine.destroyNode(self.textNode)
            self.textNode = None

    def __onSchedule(self, ID, isComplete):
        if self._scheduleId != ID:
            return

        self._scheduleId = SCHEDULE_NOT_ACTIVE

        if self.enable is True:
            self.__attachSchedule(self.timingViewTime)
            self.__updateText()

        if self.textNode is not None and self.enable is False:
            self.textNode.removeFromParent()
            Mengine.destroyNode(self.textNode)
            self.textNode = None

    def __updateText(self):
        if SceneManager.isCurrentGameScene() is False:
            return False

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return False

        if SceneManager.hasLayerScene("BlockInput"):
            layer = SceneManager.getLayerScene("BlockInput")
        else:
            layer = scene.getMainLayer()
        if layer is None:
            return False

        layerSize = layer.getSize()

        currentSceneName = SceneManager.getCurrentSceneName()
        zoomOpenGroupName = ZoomManager.getZoomOpenGroupName()
        arrowItem = ArrowManager.getArrowAttach()

        text = "Scene: "
        if currentSceneName is not None:
            text += currentSceneName

        if zoomOpenGroupName is not None:
            text += "\nZoom: " + zoomOpenGroupName

        if arrowItem is not None:
            text += '\nArrow attachment: '
            if isinstance(arrowItem, Params) is True and arrowItem.hasParam("FoundItems"):
                ItemsOnArrow = arrowItem.getParam('FoundItems')
                for itemName in ItemsOnArrow:
                    text += "\n  " + itemName
            else:
                text += "\n  " + str(arrowItem.getName())    # fix for ConstString

        if self.textNode is None:
            self.textNode = layer.createChild("TextField")
            self.textNode.setTextId("__ID_TEXT_CONSOLE")
            # self.textNode.setFontName("__CONSOLE_FONT__")
            self.textNode.setHorizontalLeftAlign()
            self.textNode.setVerticalBottomAlign()
        else:
            if self.__text == text:
                return
        self.textNode.setTextFormatArgs(text)

        textPosition = (layerSize.x * 0.03, layerSize.y * 0.03, 0.0)
        if zoomOpenGroupName is not None:
            self.textNode.setWorldPosition(textPosition)
        else:
            self.textNode.setLocalPosition(textPosition)

        self.textNode.enable()
        self.text = text

    def __onSceneInit(self, sceneName):
        if self.enable is True:
            self.__destroyNode()
            self.__updateText()
        else:
            self.__removeSchedule()
        return False

    def __onKeyEvent(self, key, x, y, isDown, isRepeat):
        if isDown is False:
            return False

        if isRepeat is True:
            return False

        if key != Mengine.KC_I:
            return False

        self.enable = not self.enable

        self.__removeSchedule()
        self.__updateText()
        self.__attachSchedule(self.timingViewTime)

        return False

    def __autoEnableForQA(self):
        self.enable = True
        self.__updateText()
        self.__attachSchedule(self.timingViewTime)
