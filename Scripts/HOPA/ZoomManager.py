from Foundation.ArrowManager import ArrowManager
from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Notification import Notification


class ZoomManager(object):
    s_activeZooms = {}
    s_zooms = {}
    allow_types = []
    ZOOM_INIT = 0
    ZOOM_ENTER = 1

    s_currentGameZoomName = None

    onZoomInitObserver = None
    onZoomEnterObserver = None
    onZoomLeaveObserver = None
    onZoomClickObserver = None
    onTransitionBeginObserver = None
    onTransitionEndObserver = None
    onSessionSaveObserver = None
    onSessionLoadObserver = None
    onSessionRemoveCompleteObserver = None

    blockOpen = False

    class Zoom(object):
        def __init__(self, object, fromSceneName, frameGroupName, immediately, zoomGroupName,
                     viewport, mask, overFrameGroupName, hasOverLayer):
            self.object = object

            self.fromSceneName = fromSceneName
            self.frameGroupName = frameGroupName
            self.immediately = immediately
            self.zoomGroupName = zoomGroupName
            self.viewport = viewport
            self.mask = mask

            self.overFrameGroupName = overFrameGroupName
            self.overLayer = hasOverLayer

            self.blockOpen = False
            self.open = False

            self.tempFrameGroupName = None
            pass

        def hasObject(self):
            return self.object is not None
            pass

        def getObject(self):
            return self.object
            pass

        def getFrameGroupName(self):
            return self.frameGroupName
            pass

        def getOverFrameGroupName(self):
            return self.overFrameGroupName
            pass

        def hasOverLayer(self):
            return self.overLayer

        def getAfterFrameGroupName(self):
            return self.AfterFrameGroup
            pass

        def getFromSceneName(self):
            return self.fromSceneName
            pass

        def setBlockOpen(self, value):
            self.blockOpen = value
            pass

        def getBlockOpen(self):
            return self.blockOpen
            pass

        def getGroupName(self):
            return self.zoomGroupName
            pass

        def setOpen(self, open):
            self.open = open
            pass

        def getOpen(self):
            return self.open
            pass

        def getImmediately(self):
            return self.immediately
            pass

        pass

    @staticmethod
    def onInitialize():
        from HOPA.Object.ObjectInventoryItem import ObjectInventoryItem
        ZoomManager.setAllowObjectTypes([ObjectInventoryItem])

        ZoomManager.onZoomInitObserver = Notification.addObserver(Notificator.onZoomInit, ZoomManager._zoomInit)
        ZoomManager.onZoomEnterObserver = Notification.addObserver(Notificator.onZoomEnter, ZoomManager._zoomEnter)
        ZoomManager.onZoomLeaveObserver = Notification.addObserver(Notificator.onZoomLeave, ZoomManager._zoomLeave)
        ZoomManager.onZoomClickObserver = Notification.addObserver(Notificator.onZoomClick, ZoomManager._zoomClick)
        ZoomManager.onTransitionBeginObserver = Notification.addObserver(Notificator.onTransitionBegin, ZoomManager.__onTransitionBegin)
        ZoomManager.onTransitionEndObserver = Notification.addObserver(Notificator.onTransitionEnd, ZoomManager.__onTransitionEnd)
        ZoomManager.onSessionSaveObserver = Notification.addObserver(Notificator.onSessionSave, ZoomManager.__onSessionSave)
        ZoomManager.onSessionLoadObserver = Notification.addObserver(Notificator.onSessionLoad, ZoomManager.__onSessionLoad)
        ZoomManager.onSessionRemoveCompleteObserver = Notification.addObserver(Notificator.onSessionRemoveComplete, ZoomManager.__onSessionRemoveComplete)
        pass

    @staticmethod
    def onFinalize():
        ZoomManager.s_activeZooms = {}
        ZoomManager.s_zooms = {}

        Notification.removeObserver(ZoomManager.onZoomInitObserver)
        Notification.removeObserver(ZoomManager.onZoomEnterObserver)
        Notification.removeObserver(ZoomManager.onZoomLeaveObserver)
        Notification.removeObserver(ZoomManager.onZoomClickObserver)
        Notification.removeObserver(ZoomManager.onTransitionBeginObserver)
        Notification.removeObserver(ZoomManager.onTransitionEndObserver)
        Notification.removeObserver(ZoomManager.onSessionSaveObserver)
        Notification.removeObserver(ZoomManager.onSessionLoadObserver)
        Notification.removeObserver(ZoomManager.onSessionRemoveCompleteObserver)
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ZoomSceneName = record.get("ZoomSceneName")
            SceneName = record.get("SceneName")
            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")
            FrameGroup = record.get("FrameGroup")
            Immediately = record.get("Immediately")
            Viewport = bool(record.get("Viewport", 1))
            Mask = record.get("Mask")
            OverFrameGroup = record.get("OverFrameGroup")
            HasOverLayer = bool(record.get("HasOverLayer", 0))

            ZoomManager.setZoom(ZoomSceneName, SceneName, GroupName, ObjectName, FrameGroup, Immediately, Viewport,
                                Mask, OverFrameGroup, HasOverLayer)
            pass

        return True
        pass

    @staticmethod
    def hasZoom(zoomGroupName):
        if zoomGroupName not in ZoomManager.s_zooms:
            return False
            pass

        return True
        pass

    @staticmethod
    def resetZoomsTempFrame():
        for zoom in ZoomManager.s_zooms.itervalues():
            zoom.tempFrameGroupName = None

    @staticmethod
    def getZoom(zoomGroupName):
        if zoomGroupName not in ZoomManager.s_zooms:
            Trace.log("Manager", 0, "ZoomManager.getZoom not found zoom %s [maybe add to Zooms.xlsx]" % (zoomGroupName))
            return None
            pass

        return ZoomManager.s_zooms[zoomGroupName]
        pass

    @staticmethod
    def setCurrentGameZoomName(zoomName):
        ZoomManager.s_currentGameZoomName = zoomName
        pass

    @staticmethod
    def getCurrentGameZoomName():
        return ZoomManager.s_currentGameZoomName
        pass

    @staticmethod
    def calcZoomPointLeft(zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)
        openZoomGroup = GroupManager.getGroup(zoomGroupName)

        mainLayer = openZoomGroup.getMainLayer()
        size = mainLayer.getSize()

        zoomPoint = None
        if zoom.hasObject() is True:
            object = zoom.getObject()
            zoomPoint = object.getPoint()
            pass

        if zoomPoint is None:
            resolution = Mengine.getContentResolution()
            screenWidth = resolution.getWidth()
            screenHeight = resolution.getHeight()

            InventorySizeY = DefaultManager.getDefaultFloat("InventorySizeY", 140)

            if zoom.mask is not None:
                InventorySizeY = 0.0
                pass

            ViewPort = Mengine.getGameViewport()

            screenHeight = screenHeight - (InventorySizeY + ViewPort.begin.y)

            zoomPoint = (screenWidth * 0.5 - size.x * 0.5, ViewPort.begin.y + (screenHeight * 0.5 - size.y * 0.5))
            pass

        return zoomPoint
        pass

    @staticmethod
    def calcZoomPointRight(zoomGroupName):
        pointLeft = ZoomManager.calcZoomPointLeft(zoomGroupName)

        zoomGroup = GroupManager.getGroup(zoomGroupName)

        mainLayer = zoomGroup.getEntity()
        ZoomSize = mainLayer.getSize()

        pointRight = (pointLeft[0] + ZoomSize.x, pointLeft[1])

        return pointRight
        pass

    @staticmethod
    def hasButtonClose(zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)

        FrameGroupName = zoom.getFrameGroupName()
        if FrameGroupName is None:
            return False
            pass

        group = GroupManager.getGroup(FrameGroupName)
        if group.hasObject("Demon_CloseZoom") is False:
            return False
            pass

        return True
        pass

    @staticmethod
    def getButtonClose(zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)
        FrameGroupName = zoom.getFrameGroupName()
        demon = GroupManager.getObject(FrameGroupName, "Demon_CloseZoom")
        button = demon.getObject("Button_CloseZoom")

        return button
        pass

    @staticmethod
    def setZoom(zoomGroupName, fromSceneName, groupName, objectName, frameGroupName, immediately, Viewport, ZoomMask,
                overFrameGroupName, hasOverLayer):
        object = None
        if groupName is not None:
            if isinstance(GroupManager.getGroup(zoomGroupName), GroupManager.EmptyGroup):
                return

            if GroupManager.hasObject(groupName, objectName) is False:
                return
                pass

            object = GroupManager.getObject(groupName, objectName)
            pass

        Zoom = ZoomManager.Zoom(object, fromSceneName, frameGroupName, immediately, zoomGroupName, Viewport, ZoomMask,
                                overFrameGroupName, hasOverLayer)

        ZoomManager.s_zooms[zoomGroupName] = Zoom
        pass

    @staticmethod
    def hasZoomGroupName(zoomObject):
        for zoom in ZoomManager.s_zooms.itervalues():
            if zoom.object is not zoomObject:
                continue
                pass

            return True
            pass

        return False
        pass

    @staticmethod
    def getZoomGroupName(zoomObject):
        for zoom in ZoomManager.s_zooms.itervalues():
            if zoom.object is not zoomObject:
                continue
                pass

            return zoom.zoomGroupName
            pass

        Trace.log("Manager", 0, "ZoomManager.getZoomGroupName not found zoom group name [%s:%s]" % (zoomObject.getGroupName(), zoomObject.getName()))

        return None
        pass

    @staticmethod
    def openZoom(zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)
        ZoomSceneName = zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName and ZoomSceneName is not None:
            return

        ZoomItemOpen = DefaultManager.getDefaultBool("ZoomItemOpen", False)
        arrow_attach_object = ArrowManager.getArrowAttach()

        if ZoomItemOpen is True and arrow_attach_object is not None:
            if type(arrow_attach_object) in ZoomManager.allow_types or len(ZoomManager.allow_types) == 0:
                InventoryItemEntity = arrow_attach_object.getEntity()
                InventoryItemEntity.place()
            elif arrow_attach_object.getName() == "ElementalMagicRing":
                pass
            else:
                return

        Notification.notify(Notificator.onZoomOpen, zoomGroupName)

        if _DEVELOPMENT is True:
            Trace.msg("<ZoomManager> open zoom '%s'" % zoomGroupName)

    @staticmethod
    def closeZoom(zoomGroupName):
        BlockGameScenes = SceneManager.isBlockGameScenes()
        if BlockGameScenes is True:
            return
            pass

        Notification.notify(Notificator.onZoomClose, zoomGroupName)
        pass

    @staticmethod
    def __onTransitionBegin(sceneFrom, sceneTo, ZoomGroupName):
        if SceneManager.isGameScene(sceneTo) is True:
            ZoomManager.setCurrentGameZoomName(ZoomGroupName)
            pass
        elif SceneManager.isGameScene(sceneFrom) is True:
            ZoomGroupName = ZoomManager.getZoomOpenGroupName()
            ZoomManager.setCurrentGameZoomName(ZoomGroupName)
            pass

        return False
        pass

    @staticmethod
    def __onTransitionEnd(sceneFrom, sceneTo, ZoomGroupName):
        if SceneManager.isGameScene(sceneTo) is True:
            ZoomManager.setCurrentGameZoomName(ZoomGroupName)
            pass

        return False
        pass

    @staticmethod
    def __onSessionSave(params):
        params["ZoomManager"] = {}

        gameZoomName = ZoomManager.getCurrentGameZoomName()
        currentZoomName = ZoomManager.getZoomOpenGroupName()

        params["ZoomManager"]["GameZoomName"] = gameZoomName
        params["ZoomManager"]["CurrentZoomName"] = currentZoomName

        return False
        pass

    @staticmethod
    def __onSessionLoad(params):
        gameZoomName = params["ZoomManager"]["GameZoomName"]
        currentZoomName = params["ZoomManager"]["CurrentZoomName"]

        ZoomManager.setCurrentGameZoomName(gameZoomName)

        return False
        pass

    @staticmethod
    def __onSessionRemoveComplete():
        ZoomManager.s_currentGameZoomName = None

        for zoom in ZoomManager.s_zooms.itervalues():
            zoom.setOpen(False)
            pass

        return False
        pass

    @staticmethod
    def _zoomInit(ZoomGroupName):
        ZoomManager.s_activeZooms[ZoomGroupName] = ZoomManager.ZOOM_INIT
        return False
        pass

    @staticmethod
    def _zoomClick(object):
        BlockOpen = object.getParam("BlockOpen")
        if BlockOpen is True:
            return False
            pass

        BlockGameScenes = SceneManager.isBlockGameScenes()
        if BlockGameScenes is True:
            return False
            pass

        if ZoomManager.blockOpen is True:
            return False

        zoomGroupName = ZoomManager.getZoomGroupName(object)
        ZoomManager.openZoom(zoomGroupName)

        return False
        pass

    @staticmethod
    def _zoomEnter(zoomGroupName):
        ZoomManager.s_activeZooms[zoomGroupName] = ZoomManager.ZOOM_ENTER

        return False
        pass

    @staticmethod
    def _zoomLeave(zoomGroupName):
        if zoomGroupName not in ZoomManager.s_activeZooms.keys():
            return False
            pass

        ZoomManager.s_activeZooms.pop(zoomGroupName)

        if len(ZoomManager.s_activeZooms) == 0:
            Notification.notify(Notificator.onZoomEmpty)
            pass

        return False
        pass

    @staticmethod
    def isZoomInit(ZoomGroupName):
        return ZoomGroupName in ZoomManager.s_activeZooms
        pass

    @staticmethod
    def isZoomEnter(ZoomGroupName):
        if ZoomGroupName not in ZoomManager.s_activeZooms:
            return False
            pass

        state = ZoomManager.s_activeZooms[ZoomGroupName]

        return state is ZoomManager.ZOOM_ENTER
        pass

    @staticmethod
    def isZoomLeave(ZoomGroupName):
        return ZoomGroupName not in ZoomManager.s_activeZooms
        pass

    @staticmethod
    def isZoomEmpty():
        return len(ZoomManager.s_activeZooms) == 0
        pass

    @staticmethod
    def getZoomOpenGroupName():
        if len(ZoomManager.s_activeZooms) > 0:
            names = ZoomManager.s_activeZooms.keys()
            return names[0]
            pass

        return None
        pass

    @staticmethod
    def getZoomOpenGroup():
        ZoomOpenGroupName = ZoomManager.getZoomOpenGroupName()

        if ZoomOpenGroupName is None:
            return None
            pass

        ZoomOpenGroup = GroupManager.getGroup(ZoomOpenGroupName)

        return ZoomOpenGroup
        pass

    @staticmethod
    def getZoomOpen():
        ZoomOpenGroupName = ZoomManager.getZoomOpenGroupName()

        if ZoomOpenGroupName is None:
            return None
            pass

        Zoom = ZoomManager.getZoom(ZoomOpenGroupName)

        return Zoom
        pass

    @staticmethod
    def getZoomObject(zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)

        if zoom is None:
            return None
            pass

        ZoomObject = zoom.getObject()

        return ZoomObject
        pass

    @staticmethod
    def getZoomEntryByObject(zoomObject):
        for zoomEntry in ZoomManager.s_zooms.itervalues():
            if zoomEntry.object == zoomObject:
                return zoomEntry

    @staticmethod
    def sceneHasZooms(sceneName):
        for zoom in ZoomManager.s_zooms.itervalues():
            if zoom.hasObject() is False:
                continue

            FromSceneName = zoom.getFromSceneName()
            if FromSceneName == sceneName:
                return True

        return False

    @staticmethod
    def getActiveSceneZooms(sceneName):
        listZooms = []
        for zoom in ZoomManager.s_zooms.itervalues():
            if zoom.hasObject() is False:
                continue
                pass
            FromSceneName = zoom.getFromSceneName()
            if FromSceneName != sceneName:
                continue
                pass

            object = zoom.getObject()

            if object.getEnable() is False:
                continue
                pass

            if object.getBlockOpen() is True:
                continue
                pass

            listZooms.append(zoom)
            pass

        return listZooms

    @staticmethod
    def getActiveSceneZoomObjects(sceneName):
        zoomObjects = []

        for zoom in ZoomManager.s_zooms.itervalues():
            if zoom.hasObject() is False:
                continue

            FromSceneName = zoom.getFromSceneName()
            if FromSceneName != sceneName:
                continue

            zoomObj = zoom.getObject()

            if zoomObj.getEnable() is False:
                continue

            if zoomObj.getBlockOpen() is True:
                continue

            zoomObjects.append(zoomObj)

        return zoomObjects

    @staticmethod
    def setAllowObjectTypes(TypeList):
        ZoomManager.allow_types = TypeList
        pass

    @staticmethod
    def getZoomPoint(zoom, zoomGroup):
        zoomMainLayer = zoomGroup.getMainLayer()
        zoomSize = zoomMainLayer.getSize()

        resolution = Mengine.getContentResolution()
        contentWidth = resolution.getWidth()
        contentHeight = resolution.getHeight()

        InventorySizeY = DefaultManager.getDefaultFloat("InventorySizeY", 140)

        if zoom.mask is not None:
            InventorySizeY = 0.0
            pass

        GameViewport = Mengine.getGameViewport()

        zoomZoneWidth = contentWidth
        zoomZoneHeight = contentHeight - (InventorySizeY + GameViewport.begin.y)

        zoomPoint = (
            zoomZoneWidth * 0.5 - zoomSize.x * 0.5,
            GameViewport.begin.y + (zoomZoneHeight * 0.5 - zoomSize.y * 0.5)
        )

        return zoomPoint

    @staticmethod
    def setBlockOpen(value):
        ZoomManager.blockOpen = bool(value)
