import Foundation.Utils as Utils
from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.ScenarioManager import ScenarioManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class SystemZoom(System):
    def _onParams(self, params):
        self.openZoomGroup = None
        self.zoomGroupName = None
        self.forceCloseZoomGroupName = None
        self.FrameGroupName = None
        self.SceneZoomEffectFactor = DefaultManager.getDefaultFloat("SceneZoomEffectFactor", 1.1)
        self.Scene_scale = ()

        self.SceneName = None

        self.front_hotspot = None
        self.back_hotspot = None
        self.object = None
        self.zoomPoint = None

        self.Zoom = None

        self.onEscPressed = None
        self.blockClose = []
        self.Opening = False

        self.fade_to = DefaultManager.getDefaultFloat("ZoomFadeTo", 0.75)
        pass

    def _onRun(self):
        self.addObserver(Notificator.onZoomOpen, self.__zoomOpen)
        self.addObserver(Notificator.onZoomClose, self.__zoomClose)
        self.addObserver(Notificator.onZoomForceOpen, self.__zoomForceOpen)
        self.addObserver(Notificator.onSceneInit, self.__sceneEnter)
        self.addObserver(Notificator.onSceneDeactivate, self.__sceneDeactivate)
        self.addObserver(Notificator.onEscPressed, self.__onPressEsc)
        self.addObserver(Notificator.onZoomBlockClose, self.__onZoomBlockClose)
        self.addObserver(Notificator.onInterruption, self.__onInterruption)

        self.addObserver(Notificator.onZoomEnigmaChangeFrameGroup, self.__onZoomEnigmaChangeFrameGroup)
        self.addObserver(Notificator.onZoomEnigmaChangeBackFrameGroup, self.__onZoomEnigmaChangeBackFrameGroup)

        return True
        pass

    def _onStop(self):
        ZoomManager.resetZoomsTempFrame()

        if self.zoomGroupName is None:
            return
            pass

        self.cleanData(True)
        pass

    def __onInterruption(self):
        if self.Opening is True:
            return False
            pass

        if self.forceCloseZoomGroupName is not None:
            return False
            pass

        if self.zoomGroupName is None:
            return False
            pass

        self.forceCloseZoomGroupName = self.zoomGroupName

        self.cleanData()

        Notification.notify(Notificator.onZoomLeave, self.forceCloseZoomGroupName)

        self.zoomGroupName = None

        return False
        pass

    def __sceneDeactivate(self, sceneName):
        if self.forceCloseZoomGroupName is not None:
            return False

        if self.zoomGroupName is None:
            return False

        self.forceCloseZoomGroupName = self.zoomGroupName

        self.cleanData()

        Notification.notify(Notificator.onZoomLeave, self.forceCloseZoomGroupName)

        self.zoomGroupName = None

        return False

    def __sceneEnter(self, sceneName):
        if self.forceCloseZoomGroupName is None:
            # if self.zoomGroupName is not None:
            #     self.forceCloseZoomGroupName = self.zoomGroupName
            #     Notification.notify(Notificator.onZoomLeave, self.forceCloseZoomGroupName)
            #     self.cleanData()
            #     self.zoomGroupName = None
            #     pass
            return False
            pass

        if SceneManager.getCurrentGameSceneName() != sceneName:
            return False
            pass

        Zoom = ZoomManager.getZoom(self.forceCloseZoomGroupName)
        ZoomObject = Zoom.getObject()

        if ZoomObject.getEnd() is True:
            # do not open zooms that are ended
            self.cleanData()
            Notification.notify(Notificator.onZoomLeave, self.forceCloseZoomGroupName)
            self.forceCloseZoomGroupName = None
            return False

        ForceZoomScene = Zoom.getFromSceneName()
        if ForceZoomScene == sceneName:
            ZoomManager.openZoom(self.forceCloseZoomGroupName)
            pass

        if SceneManager.isGameScene(sceneName) is True:
            self.forceCloseZoomGroupName = None
            pass

        return False
        pass

    def _onSave(self):
        return [self.zoomGroupName, self.SceneName, self.blockClose]
        pass

    def _onLoad(self, data_save):
        zoomGroupName, SceneName, self.blockClose = data_save

        return False
        pass

    def __onZoomEnigmaChangeFrameGroup(self, zoomFrameGroup):
        if self.existTaskChain("ZoomChangeGroupName"):
            return False
            pass

        OldFrameGroupName = self.FrameGroupName

        if self.Zoom is None:
            return False

        if self.Zoom.tempFrameGroupName == zoomFrameGroup:
            return False

        self.Zoom.tempFrameGroupName = zoomFrameGroup

        def __scopeChangeFrame(source):
            self.FrameGroupName = zoomFrameGroup

            FrameGroup = GroupManager.getGroup(zoomFrameGroup)
            frameScene = FrameGroup.getScene()

            frameLayer = FrameGroup.getMainLayer()
            frameSize = frameLayer.getSize()

            group = GroupManager.getGroup(OldFrameGroupName)
            scene = group.getScene()
            layer = group.getMainLayer()
            localPosition = layer.getLocalPosition()

            # print " LOCAL POSITION {}".format(localPosition)
            # print " LOCAL POSITION 1={} 2={}".format((frameSize.x * 0.5, frameSize.y * 0.5), frameLayer.getLocalPosition())

            # frameLayer.setLocalPosition((frameSize.x * 0.5, frameSize.y * 0.5))
            frameLayer.setLocalPosition(localPosition)

            # frameLayer.setOrigin((frameSize.x * 0.5, frameSize.y * 0.5))
            origin = layer.getOrigin()
            frameLayer.setOrigin(origin)
            frameLayer.setScale((1.0, 1.0, 1.0))
            frameLayerRender = frameLayer.getRender()
            frameLayerRender.setLocalAlpha(1.0)

            frameSceneLocalPosition = scene.getLocalPosition()
            frameScene.setLocalPosition(frameSceneLocalPosition)

            if self.Zoom.hasOverLayer() is True:
                self.__attachOverLayer()

            CurrentSceneName = SceneManager.getCurrentSceneName()

            timeOpen = 400

            with GuardBlockInput(source) as guard_tc:
                HideFrameGroup = GroupManager.getGroup(OldFrameGroupName)
                HideFrameLayer = HideFrameGroup.getMainLayer()

                ShowFrameGroup = GroupManager.getGroup(zoomFrameGroup)
                ShowFrameLayer = ShowFrameGroup.getMainLayer()

                with guard_tc.addParallelTask(2) as (tc_show, tc_hide):
                    tc_show.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                    LayerName=zoomFrameGroup, Value=True)
                    tc_show.addTask("TaskNodeAlphaTo", Node=ShowFrameLayer, From=0, To=1.0, Time=timeOpen)

                    def _check(layer):
                        if layer.isActivate() is False:
                            return False

                        return True

                    with tc_hide.addIfTask(_check, HideFrameLayer) as (tc_true, tc_false):
                        tc_true.addTask("TaskNodeAlphaTo", Node=HideFrameLayer, From=1, To=0, Time=timeOpen)

                    tc_hide.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                    LayerName=OldFrameGroupName, Value=False)
            pass

        with self.createTaskChain(Name="ZoomChangeGroupName", Cb=self.__openZoomAfterFadeIn) as tc:
            if OldFrameGroupName is None:
                tc.addTask("TaskZoomEnter")

            tc.addScope(__scopeChangeFrame)

        return False
        pass

    def __onZoomEnigmaChangeBackFrameGroup(self):
        if self.existTaskChain("ZoomChangeBackGroupName"):
            return False
            pass

        if self.Zoom is None:
            return False

        OldFrameGroupName = self.FrameGroupName

        zoomFrameGroup = self.Zoom.getFrameGroupName()

        self.Zoom.tempFrameGroupName = None

        def __scopeChangeFrame(source):
            self.FrameGroupName = zoomFrameGroup

            FrameGroup = GroupManager.getGroup(zoomFrameGroup)

            frameLayer = FrameGroup.getMainLayer()
            frameSize = frameLayer.getSize()

            frameScene = FrameGroup.getScene()

            frameLayer.setLocalPosition((frameSize.x * 0.5, frameSize.y * 0.5))

            frameLayer.setOrigin((frameSize.x * 0.5, frameSize.y * 0.5))
            frameLayer.setScale((1.0, 1.0, 1.0))
            frameLayerRender = frameLayer.getRender()
            frameLayerRender.setLocalAlpha(0.0)

            oldFrameGroup = GroupManager.getGroup(OldFrameGroupName)
            oldFrameScene = oldFrameGroup.getScene()
            oldFrameScenePosition = oldFrameScene.getLocalPosition()

            frameScene.setLocalPosition(oldFrameScenePosition)

            if self.Zoom.hasOverLayer() is True:
                self.__attachOverLayer()

            CurrentSceneName = SceneManager.getCurrentSceneName()

            timeOpen = 400

            with GuardBlockInput(source) as guard_tc:
                HideFrameGroup = GroupManager.getGroup(OldFrameGroupName)
                HideFrameLayer = HideFrameGroup.getMainLayer()

                ShowFrameGroup = GroupManager.getGroup(zoomFrameGroup)
                ShowFrameLayer = ShowFrameGroup.getMainLayer()

                with guard_tc.addParallelTask(2) as (tc_show, tc_hide):
                    tc_show.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                    LayerName=zoomFrameGroup, Value=True)
                    tc_show.addTask("TaskNodeAlphaTo", Node=ShowFrameLayer, From=0, To=1.0, Time=timeOpen)

                    tc_hide.addTask("TaskNodeAlphaTo", Node=HideFrameLayer, To=0, Time=timeOpen)
                    tc_hide.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                    LayerName=OldFrameGroupName, Value=False)
            pass

        with self.createTaskChain(Name="ZoomChangeBackGroupName", Cb=self.__openZoomAfterFadeIn) as tc:
            if OldFrameGroupName is None:
                tc.addTask("TaskZoomEnter")

            tc.addScope(__scopeChangeFrame)

        return False
        pass

    def __onZoomBlockClose(self, zoomGroupName, value):
        if value is True:
            if zoomGroupName in self.blockClose:
                return False
            self.blockClose.append(zoomGroupName)
            pass

        elif value is False:
            if zoomGroupName in self.blockClose:
                self.blockClose.remove(zoomGroupName)
                pass
            pass

        return False
        pass

    def __zoomForceOpen(self, zoomGroupName):
        timeOpen = 0.01
        timeOpen *= 1000  # speed fix
        self.__playOpen(zoomGroupName, timeOpen)
        return False
        pass

    def __zoomOpen(self, zoomGroupName):
        ZoomSpeed = DefaultManager.getDefaultFloat("ZoomOpenSpeed", 25.0)
        timeOpen = ZoomSpeed / 100
        timeOpen *= 1000  # speed fix
        self.__playOpen(zoomGroupName, timeOpen)
        return False
        pass

    def __playOpen(self, zoomGroupName, timeOpen):
        if self.existTaskChain("ZoomClose") or self.existTaskChain("ZoomOpen"):
            return False
            pass

        self.Opening = True

        ZoomItemOpen = DefaultManager.getDefaultBool("ZoomItemOpen", False)

        if ZoomManager.hasZoom(zoomGroupName) is False:
            Trace.log("SystemZoom.__playOpen not found zoom %s" % (zoomGroupName))

            return False
            pass

        self.Zoom = ZoomManager.getZoom(zoomGroupName)

        if self.Zoom.hasObject() is True:
            ZoomObject = self.Zoom.getObject()

            if ZoomObject.isActive() is False:
                Trace.log("SystemZoom.__playOpen zoom %s object %s:%s is not entity" % (
                    zoomGroupName, ZoomObject.getGroupName(), ZoomObject.getName()))

                return False
                pass
            pass
        self.Zoom.setOpen(True)

        self.openZoomGroup = GroupManager.getGroup(zoomGroupName)
        self.zoomGroupName = zoomGroupName

        if self.Zoom.tempFrameGroupName is None:
            self.FrameGroupName = self.Zoom.getFrameGroupName()
        else:
            self.FrameGroupName = self.Zoom.tempFrameGroupName

        self.openZoomGroup.onActivate()
        self.openZoomGroup.onEnable()

        zoomScene = self.openZoomGroup.getScene()
        zoomMainLayer = self.openZoomGroup.getMainLayer()

        self.zoomPoint = None
        if self.Zoom.hasObject() is True:
            self.object = self.Zoom.getObject()
            self.zoomPoint = self.object.getPoint()
            pass

        DefaultZoomPoint = ZoomManager.getZoomPoint(self.Zoom, self.openZoomGroup)

        if self.zoomPoint is None:
            self.zoomPoint = DefaultZoomPoint
            pass

        ZoomOffset = (self.zoomPoint[0] - DefaultZoomPoint[0], self.zoomPoint[1] - DefaultZoomPoint[1])

        # self.FrameGroupName = self.Zoom.getFrameGroupName()

        hav_Dem_A = self.openZoomGroup.hasObject("Demon_ZoomAfterFrame")

        if self.Zoom.hasObject() is True:
            ZoomObject = self.Zoom.getObject()
            ZoomEntity = ZoomObject.getEntity()
            ZoomHotSpot = ZoomEntity.getHotSpot()

            zoomSize = zoomMainLayer.getSize()

            zoomMainLayer.setLocalPosition((zoomSize.x * 0.5, zoomSize.y * 0.5))
            zoomMainLayer.setOrigin((zoomSize.x * 0.5, zoomSize.y * 0.5))
            zoomMainLayer.setScale((0.01, 0.01, 0.01))
            zoomMainLayerRender = zoomMainLayer.getRender()
            zoomMainLayerRender.setLocalAlpha(0.01)

            hs_center = ZoomHotSpot.getWorldPolygonCenter()

            PosScene = (hs_center.x - zoomSize.x * 0.5, hs_center.y - zoomSize.y * 0.5)
            zoomScene.setLocalPosition(PosScene)

            if self.FrameGroupName is not None and hav_Dem_A is False:
                FrameGroup = GroupManager.getGroup(self.FrameGroupName)
                frameScene = FrameGroup.getScene()

                frameLayer = FrameGroup.getMainLayer()
                frameSize = frameLayer.getSize()

                frameLayer.setLocalPosition((frameSize.x * 0.5, frameSize.y * 0.5))
                frameLayer.setOrigin((frameSize.x * 0.5, frameSize.y * 0.5))
                frameLayer.setScale((0.01, 0.01, 0.01))
                frameLayerRender = frameLayer.getRender()
                frameLayerRender.setLocalAlpha(0.01)

                PosFrameScene = (hs_center.x - frameSize.x * 0.5, hs_center.y - frameSize.y * 0.5)

                frameScene.setLocalPosition(PosFrameScene)

                if self.Zoom.hasOverLayer() is True:
                    self.__attachOverLayer()

                pass

            self.OverFrameGroupName = self.Zoom.getOverFrameGroupName()
            if self.OverFrameGroupName is not None and hav_Dem_A is False:  # 'hav_Dem_A is False' -> create zoom viewport
                OverFrameGroup = GroupManager.getGroup(self.OverFrameGroupName)
                OverFrameGroupScene = OverFrameGroup.getScene()

                OverFrameLayer = OverFrameGroup.getMainLayer()
                OverFrameSize = OverFrameLayer.getSize()

                OverFrameLayer.setLocalPosition((OverFrameSize.x * 0.5, OverFrameSize.y * 0.5))
                OverFrameLayer.setOrigin((OverFrameSize.x * 0.5, OverFrameSize.y * 0.5))
                OverFrameLayer.setScale((0.01, 0.01, 0.01))
                OverFrameLayerRender = OverFrameLayer.getRender()
                OverFrameLayerRender.setLocalAlpha(0.01)

                PosFrameScene = (hs_center.x - OverFrameSize.x * 0.5, hs_center.y - OverFrameSize.y * 0.5)
                OverFrameGroupScene.setLocalPosition(PosFrameScene)
                pass
            pass
        else:
            zoomMainLayer.setLocalPosition(self.zoomPoint)
            pass

        viewport = ((0.0, 0.0), (zoomSize.x, zoomSize.y))

        hasViewport = DefaultManager.getDefaultBool("ZoomViewport", True)

        if hav_Dem_A is False:
            if hasViewport is True and self.Zoom.viewport is True:
                zoomMainLayer.setViewport(viewport)
                pass
            pass

        if self.Zoom.mask is not None:
            Mask = Mengine.getResourceReference(self.Zoom.mask)
            zoomMainLayer.setImageMask(Mask)
            pass

        def __unhideMainLayer():
            zoomMainLayerRender = zoomMainLayer.getRender()
            zoomMainLayerRender.setLocalAlpha(1.0)
            pass

        fadeTime = timeOpen  # * 0.5
        fadeTo = self.fade_to

        zoom_easing_in = DefaultManager.getDefault("ZoomTweenIn", "easyLinear")

        CurrentSceneName = SceneManager.getCurrentSceneName()

        with self.createTaskChain(Name="ZoomOpen", Cb=self.__openZoomAfterFadeIn) as tc:
            tc.addTask("TaskSceneEntering")

            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addFunction(__unhideMainLayer)
                guard_tc.addNotify(Notificator.onZoomInit, self.zoomGroupName)
                if self.Zoom.hasObject() is True:
                    def _zoomMainLayerOpen(source):
                        with source.addParallelTask(5) as (tc1, tc2, tc3, tc4, tc_SceneZoom):
                            tc_SceneZoom.addScope(self._scope_scene_Zoom_effect, timeOpen)
                            tc1.addTask("TaskNodeScaleTo", Node=zoomMainLayer, To=(1.0, 1.0, 1.0), Time=timeOpen,
                                        Easing=zoom_easing_in)
                            tc2.addTask("TaskNodeAlphaTo", Node=zoomMainLayer, From=0.0, To=1.0, Time=timeOpen,
                                        Easing=zoom_easing_in)
                            tc3.addTask("AliasFadeIn", FadeGroupName="FadeZoom", To=fadeTo, Time=fadeTime,
                                        ReturnItem=not ZoomItemOpen, Easing=zoom_easing_in)
                            tc4.addTask("TaskNodeMoveTo", Node=zoomScene, To=self.zoomPoint, Time=timeOpen,
                                        Easing=zoom_easing_in)
                            pass
                        pass

                    def _frameGroupOpen(source):
                        FrameGroup = GroupManager.getGroup(self.FrameGroupName)
                        frameScene = FrameGroup.getScene()
                        frameLayer = FrameGroup.getMainLayer()

                        ZoomFrameGroupsPositionAuto = DefaultManager.getDefaultBool("ZoomFrameGroupsPositionAuto",
                                                                                    False)

                        if ZoomFrameGroupsPositionAuto is True:
                            framePoint = ZoomManager.getZoomPoint(self.Zoom, FrameGroup)
                        else:
                            framePoint = ZoomOffset

                        source.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                       LayerName=self.FrameGroupName, Value=True)
                        with source.addParallelTask(3) as (tc1, tc2, tc3):
                            tc1.addTask("TaskNodeScaleTo", Node=frameLayer, To=(1.0, 1.0, 1.0), Time=timeOpen,
                                        Easing=zoom_easing_in)

                            tc2.addTask("TaskNodeMoveTo", Node=frameScene, To=framePoint, Time=timeOpen,
                                        Easing=zoom_easing_in)

                            tc3.addTask("TaskNodeAlphaTo", Node=frameLayer, From=0.0, To=1.0, Time=timeOpen,
                                        Easing=zoom_easing_in)

                    def _overFrameGroupOpen(source):
                        OverFrameGroup = GroupManager.getGroup(self.OverFrameGroupName)
                        frameScene = OverFrameGroup.getScene()
                        frameLayer = OverFrameGroup.getMainLayer()

                        ZoomFrameGroupsPositionAuto = DefaultManager.getDefaultBool("ZoomFrameGroupsPositionAuto", False)

                        if ZoomFrameGroupsPositionAuto is True:
                            overFramePoint = ZoomManager.getZoomPoint(self.Zoom, OverFrameGroup)
                        else:
                            overFramePoint = ZoomOffset

                        source.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                       LayerName=self.OverFrameGroupName, Value=True)
                        with source.addParallelTask(3) as (tc1, tc2, tc3):
                            tc1.addTask("TaskNodeScaleTo", Node=frameLayer,
                                        To=(1.0, 1.0, 1.0), Time=timeOpen, Easing=zoom_easing_in)

                            # tc2.addTask("TaskNodeMoveTo", Node=frameScene, To=ZoomOffset, Time=timeOpen)
                            tc2.addTask("TaskNodeMoveTo", Node=frameScene, To=overFramePoint, Time=timeOpen,
                                        Easing=zoom_easing_in)

                            tc3.addTask("TaskNodeAlphaTo", Node=frameLayer, From=0.0, To=1.0, Time=timeOpen,
                                        Easing=zoom_easing_in)

                    parallels = [_zoomMainLayerOpen]

                    if self.FrameGroupName is not None:
                        parallels.append(_frameGroupOpen)

                    if self.OverFrameGroupName is not None:
                        parallels.append(_overFrameGroupOpen)

                    for parallel, tc_parallel in guard_tc.addParallelTaskList(parallels):
                        parallel(tc_parallel)

                    # = DEBUG =============================================================================================================
                    def __mask_debug(scope):
                        parent = zoomScene.getParent()

                        arrow = Mengine.getArrow()
                        arrow_node = arrow.getNode()
                        arrow_node.addChild(zoomScene)

                        zoomScene.setLocalPosition((-zoomSize.x * 0.5, -zoomSize.y * 0.5))

                        scope.addTask("TaskMouseButtonClick")
                        scope.addFunction(zoomScene.removeFromParent)
                        scope.addFunction(parent.addChild, zoomScene)
                        scope.addFunction(zoomScene.setLocalPosition, self.zoomPoint)
                        pass

                    do_test = DefaultManager.getDefaultBool('IMAGE_MASK_TEST', False)

                    if do_test is True:
                        guard_tc.addScope(__mask_debug)
                    # = DEBUG =============================================================================================================
                    pass
                else:
                    guard_tc.addTask("AliasFadeIn", FadeGroupName="FadeZoom", To=fadeTo, Time=fadeTime,
                                     ReturnItem=not ZoomItemOpen)

                    if self.FrameGroupName is not None:
                        guard_tc.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                         LayerName=self.FrameGroupName, Value=True)
                        pass

                    if self.OverFrameGroupName is not None:
                        guard_tc.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                         LayerName=self.OverFrameGroupName, Value=True)
                        pass
                    pass
                pass

            tc.addTask("TaskSceneLeaving")
            pass

        return False
        pass

    def __attachOverLayer(self):
        zoomScene = self.openZoomGroup.getScene()

        # print " SCENE=", zoomScene.getName()

        overLayer = self.openZoomGroup.getLayer('Layer2D_Over')
        if overLayer is None:
            return
            pass

        FrameGroup = GroupManager.getGroup(self.FrameGroupName)

        frameLayer = FrameGroup.getMainLayer()

        frameLayer.addChild(overLayer)

    def __openZoomAfterFadeIn(self, isSkip):
        if self.openZoomGroup is None:
            return
            pass

        if isSkip is True:
            return
            pass

        ZoomAutoHotspot = DefaultManager.getDefaultBool("ZoomAutoHotspot", False)

        scene = SceneManager.getCurrentScene()
        zoomScene = self.openZoomGroup.getScene()
        zoomMainLayer = self.openZoomGroup.getMainLayer()

        # remove old zoom frame (bug: https://wonderland-games.atlassian.net/browse/HO2-180)
        if self.front_hotspot is not None:
            self.front_hotspot.removeFromParent()
        if self.back_hotspot is not None:
            self.back_hotspot.removeFromParent()

        if self.FrameGroupName is None or ZoomAutoHotspot is True:
            self.front_hotspot = Mengine.createNode("HotSpotPolygon")
            front_hotspot_polygon = Utils.createPolygonScene(zoomMainLayer, 0, 0)
            self.front_hotspot.setPolygon(front_hotspot_polygon)

            self.back_hotspot = Mengine.createNode("HotSpotPolygon")
            back_hotspot_polygon = Utils.createPolygonScene(scene.main_layer, self.zoomPoint[0], self.zoomPoint[1])
            self.back_hotspot.setPolygon(back_hotspot_polygon)
            pass
        else:  # Dinamic Frames
            if GroupManager.hasObject(self.FrameGroupName, "Socket_Front"):
                Socket_Front = GroupManager.getObject(self.FrameGroupName, "Socket_Front")
                pass
            else:
                DemonFrame = GroupManager.getObject(self.FrameGroupName, "Demon_ZoomFrame")
                Socket_Front = DemonFrame.getObject("Socket_Front")
                pass

            Socket_Back = GroupManager.getObject(self.FrameGroupName, "Socket_Back")
            Socket_Back.setBlock(True)

            self.back_hotspot = Socket_Back.getEntity().getHotSpot()
            self.front_hotspot = Socket_Front.getEntity().getHotSpot()
            pass

        self.front_hotspot.setEventListener(onHandleMouseButtonEvent=self._onFrontMouseButtonEvent)
        self.front_hotspot.enable()

        self.back_hotspot.setEventListener(onHandleMouseButtonEvent=self._onBackMouseButtonEvent)
        self.back_hotspot.enable()

        zoomScene.addChildFront(self.front_hotspot)
        zoomScene.addChildFront(self.back_hotspot)

        if self.FrameGroupName is not None and ZoomAutoHotspot is False:
            if not GroupManager.hasObject(self.FrameGroupName, "Demon_ZoomFrame"):
                ZoomFrameGroupsPositionAuto = DefaultManager.getDefaultBool("ZoomFrameGroupsPositionAuto", False)

                if ZoomFrameGroupsPositionAuto is True:
                    FrameGroup = GroupManager.getGroup(self.FrameGroupName)
                    framePoint = ZoomManager.getZoomPoint(self.Zoom, FrameGroup)

                    self.front_hotspot.setWorldPosition(framePoint)
                else:
                    self.front_hotspot.setWorldPosition((0, 0))
                pass

            self.back_hotspot.setWorldPosition((0, 0))
            pass

        Notification.notify(Notificator.onZoomEnter, self.zoomGroupName)
        self.Opening = False
        pass

    def _onFrontMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        return True
        pass

    def _onBackMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        if self.object is not None:
            if TransitionManager.isBlockTransition() is True:
                return False
                pass
            pass

        if button == 0 and isDown == 1 and ArrowManager.emptyArrowAttach() is True:
            ZoomManager.closeZoom(self.zoomGroupName)
            return True
            pass

        return True
        pass

    def __zoomClose(self, zoomGroupName):
        if zoomGroupName in self.blockClose:
            return False
            pass

        if self.zoomGroupName != zoomGroupName:
            return False
            pass

        if self.existTaskChain("ZoomForceOpen") is True:
            return False
            pass

        if self.existTaskChain("ZoomOpen") is True:
            return False
            pass

        if self.existTaskChain("ZoomClose") is True:
            return False
            pass

        ZoomCloseMove = DefaultManager.getDefaultBool("ZoomCloseMove", True)
        hav_Dem_A = self.openZoomGroup.hasObject("Demon_ZoomAfterFrame")

        CurrentSceneName = SceneManager.getCurrentSceneName()

        zoom_easing_out = DefaultManager.getDefault("ZoomTweenOut", "easyLinear")

        with self.createTaskChain(Name="ZoomClose", Cb=self.__closeZoom, CbArgs=(self.zoomGroupName,)) as tc:
            with GuardBlockInput(tc) as guard_tc:
                ZoomSpeed = DefaultManager.getDefaultFloat("ZoomCloseSpeed", DefaultManager.getDefaultFloat("ZoomOpenSpeed", 25.0))
                debug_Time = 1
                timeScaleTo = ZoomSpeed / 100
                timeScaleTo *= 1000 * debug_Time  # speed fix

                timeMoveTo = ZoomSpeed / 100
                timeMoveTo *= 1000 * debug_Time  # speed fix

                # timeAlphaTo = 0.15
                timeAlphaTo = ZoomSpeed / 100
                timeAlphaTo *= 1000 * debug_Time  # speed fix

                timeFadeOut = ZoomSpeed / 100
                timeFadeOut *= 1000 * debug_Time  # speed fix

                if ZoomCloseMove is True and self.Zoom.hasObject() is True:
                    zoomScene = self.openZoomGroup.getScene()
                    zoomMainLayer = self.openZoomGroup.getMainLayer()

                    ZoomObject = self.Zoom.getObject()
                    ZoomEntity = ZoomObject.getEntity()
                    ZoomHotSpot = ZoomEntity.getHotSpot()

                    zoomSize = zoomMainLayer.getSize()

                    hs_center = ZoomHotSpot.getWorldPolygonCenter()
                    PosScene = (hs_center.x - zoomSize.x * 0.5, hs_center.y - zoomSize.y * 0.5)

                    def _zoomMainLayerClose(source):
                        with source.addParallelTask(5) as (tc0, tc1, tc2, tc3, tc_SceneZoom):
                            tc_SceneZoom.addScope(self._scope_scene_Zoom_Back_effect, timeAlphaTo)
                            tc0.addTask("TaskNodeScaleTo", Node=zoomMainLayer, To=(0.0, 0.0, 0.0), Time=timeScaleTo,
                                        Easing=zoom_easing_out)
                            tc1.addTask("TaskNodeMoveTo", Node=zoomScene, To=PosScene, Time=timeMoveTo,
                                        Easing=zoom_easing_out)
                            tc2.addTask("TaskNodeAlphaTo", Node=zoomMainLayer, To=0.0, Time=timeAlphaTo,
                                        Easing=zoom_easing_out)
                            tc3.addTask("AliasFadeOut", FadeGroupName="FadeZoom", From=self.fade_to, Time=timeFadeOut,
                                        Easing=zoom_easing_out)
                            pass
                        pass

                    def _frameGroupClose(source):
                        FrameGroup = GroupManager.getGroup(self.FrameGroupName)
                        frameScene = FrameGroup.getScene()

                        frameLayer = FrameGroup.getMainLayer()
                        frameSize = frameLayer.getSize()

                        PosFrameScene = (hs_center.x - frameSize.x * 0.5, hs_center.y - frameSize.y * 0.5)

                        with source.addParallelTask(4) as (tc1, tc2, tc3, tc4):
                            tc1.addTask("TaskNodeScaleTo", Node=frameLayer, To=(0.0, 0.0, 0.0), Time=timeScaleTo,
                                        Easing=zoom_easing_out)
                            tc2.addTask("TaskNodeMoveTo", Node=zoomScene, To=PosScene, Time=timeMoveTo,
                                        Easing=zoom_easing_out)
                            tc3.addTask("TaskNodeMoveTo", Node=frameScene, To=PosFrameScene, Time=timeMoveTo,
                                        Easing=zoom_easing_out)
                            tc4.addTask("TaskNodeAlphaTo", Node=frameLayer, To=0.0, Time=timeAlphaTo,
                                        Easing=zoom_easing_out)
                            pass
                        pass

                    def _overFrameGroupClose(source):
                        OverFrameGroup = GroupManager.getGroup(self.OverFrameGroupName)
                        frameScene = OverFrameGroup.getScene()

                        frameLayer = OverFrameGroup.getMainLayer()
                        frameSize = frameLayer.getSize()

                        PosFrameScene = (hs_center.x - frameSize.x * 0.5, hs_center.y - frameSize.y * 0.5)

                        with source.addParallelTask(4) as (tc1, tc2, tc3, tc4):
                            tc1.addTask("TaskNodeScaleTo", Node=frameLayer, To=(0.0, 0.0, 0.0), Time=timeScaleTo,
                                        Easing=zoom_easing_out)
                            tc2.addTask("TaskNodeMoveTo", Node=zoomScene, To=PosScene, Time=timeMoveTo,
                                        Easing=zoom_easing_out)
                            tc3.addTask("TaskNodeMoveTo", Node=frameScene, To=PosFrameScene, Time=timeMoveTo,
                                        Easing=zoom_easing_out)
                            tc4.addTask("TaskNodeAlphaTo", Node=frameLayer, To=0.0, Time=timeAlphaTo,
                                        Easing=zoom_easing_out)
                            pass
                        pass

                    parallels = [_zoomMainLayerClose]

                    if self.FrameGroupName is not None and hav_Dem_A is False:
                        parallels.append(_frameGroupClose)

                    if self.OverFrameGroupName is not None:
                        parallels.append(_overFrameGroupClose)

                    for parallel, tc_parallel in guard_tc.addParallelTaskList(parallels):
                        parallel(tc_parallel)
                        pass
                    pass
                else:
                    guard_tc.addTask("AliasFadeOut", FadeGroupName="FadeZoom", Time=timeFadeOut, From=self.fade_to)
                    pass

                if self.FrameGroupName is not None:
                    guard_tc.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                     LayerName=self.FrameGroupName, Value=False)
                    pass

                if self.OverFrameGroupName is not None:
                    guard_tc.addTask("TaskSceneLayerGroupEnable", SceneName=CurrentSceneName,
                                     LayerName=self.OverFrameGroupName, Value=False)
                    pass

                guard_tc.addTask("TaskSceneEntering")
                pass
            pass

        return False
        pass

    def _scope_scene_Zoom_effect(self, source, timeOpen):
        CurrentScene = SceneManager.getCurrentScene()

        if CurrentScene is None:
            return

        MainLayer = CurrentScene.getMainLayer()

        self.Scene_scale = MainLayer.getScale()
        cur_scale = MainLayer.getScale()

        scale_to = (
            cur_scale[0] * self.SceneZoomEffectFactor,
            cur_scale[1] * self.SceneZoomEffectFactor,
            cur_scale[2] * self.SceneZoomEffectFactor,
        )

        ZoomObject = self.Zoom.getObject()
        ZoomEntity = ZoomObject.getEntity()
        ZoomHotSpot = ZoomEntity.getHotSpot()
        point = ZoomHotSpot.getWorldPolygonCenter()

        with source.addFork() as fork:
            fork.addTask("TaskNodeSetPosition", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeSetOrigin", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeScaleTo", Node=MainLayer, To=scale_to, Time=timeOpen)
            pass
        pass

    def _scope_scene_Zoom_Back_effect(self, source, timeOpen):
        CurrentScene = SceneManager.getCurrentScene()

        if CurrentScene is None:
            return

        MainLayer = CurrentScene.getMainLayer()

        # cur_scale = MainLayer.getScale()
        #
        # scale_from = (
        #     cur_scale[0] * (1/self.ZoomEffectZoomFactor),
        #     cur_scale[1] * (1/self.ZoomEffectZoomFactor),
        #     cur_scale[2] * (1/self.ZoomEffectZoomFactor),
        # )

        ZoomObject = self.Zoom.getObject()
        ZoomEntity = ZoomObject.getEntity()
        ZoomHotSpot = ZoomEntity.getHotSpot()
        point = ZoomHotSpot.getWorldPolygonCenter()
        # print "_scope_scene_ZoomBack_ scale_from", self.Scene_scale,point
        with source.addFork() as fork:
            fork.addTask("TaskNodeSetPosition", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeSetOrigin", Node=MainLayer, Value=point)
            fork.addTask("TaskNodeScaleTo", Node=MainLayer, To=self.Scene_scale, Time=timeOpen)
            pass
        pass

    def __closeZoom(self, isSkip, zoomGroupName):
        if isSkip is True:
            return
            pass

        self.cleanData()

        Notification.notify(Notificator.onZoomLeave, zoomGroupName)

        pass

    def cleanData(self, force=False):
        if self.Zoom is None:
            return
            pass

        self.Zoom.setOpen(False)

        self.Opening = False

        SceneName = self.Zoom.getFromSceneName()
        Scenarios = ScenarioManager.getSceneRunScenarios(SceneName, self.zoomGroupName)

        self.zoomGroupName = None
        self.Zoom = None

        for ScenarioRunner in Scenarios:
            ScenarioRunner.skip()
            pass

        if force is False:
            self.openZoomGroup.onDisable()

            if self.openZoomGroup.isActive() is True:
                self.openZoomGroup.onDeactivate()
                pass
            frameGroup = GroupManager.getGroup(self.FrameGroupName)
            frameGroup.onDisable()
            pass

        self.openZoomGroup = None

        self.SceneName = None

        ZoomAutoHotspot = DefaultManager.getDefaultBool("ZoomAutoHotspot", False)

        if self.front_hotspot is not None:
            self.front_hotspot.removeFromParent()
            self.front_hotspot.setEventListener(onHandleMouseButtonEvent=None)

            if self.FrameGroupName is None or ZoomAutoHotspot is True:
                Mengine.destroyNode(self.front_hotspot)
                self.front_hotspot = None
                pass
            pass

        if self.back_hotspot is not None:
            self.back_hotspot.removeFromParent()
            self.back_hotspot.setEventListener(onHandleMouseButtonEvent=None)

            if self.FrameGroupName is None or ZoomAutoHotspot is True:
                Mengine.destroyNode(self.back_hotspot)
                self.back_hotspot = None
                pass
            pass

        self.front_hotspot = None
        self.back_hotspot = None
        self.FrameGroupName = None
        self.object = None

        self.zoomPoint = None
        pass

    pass

    def __onPressEsc(self, layerName):
        if layerName != "Zoom":
            return False
            pass

        if ZoomManager.isZoomEmpty() is True:
            return False
            pass

        if self.zoomGroupName != ZoomManager.getZoomOpenGroupName():
            return False
            pass

        ZoomManager.closeZoom(self.zoomGroupName)

        return False
        pass

    pass
