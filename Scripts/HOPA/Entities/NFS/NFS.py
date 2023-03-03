from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.NFSManager import NFSManager


Enigma = Mengine.importEntity("Enigma")

PI = 3.14159265

min_speed = 0.05
max_speed = 0.25


class NFS(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction(Type, "ProgressBar")
        pass

    def __init__(self):
        super(NFS, self).__init__()

        self.NFS = None

        self.SceneTiles = None

        self.CameraFollow = None
        self.CameraOffset = None

        self.CoachEntity = None

        self.Socket_CoachEntity = None
        self.Socket_Coach1Entity = None
        self.Socket_Coach2Entity = None

        self.onAffectorTimingId = None
        self.onCollisionTimingId = None

        self.CoachFollowInterpolatorId = None
        self.CameraFollowInterpolatorId = None
        self.CoachSpeedDownInterpolatorId = None
        self.CoachSpeedUpInterpolatorId = None

        self.CameraState = None

        self.pitstops = []
        self.check_pitstops = []

        self.progressbar_pitstop_offset = 0.0

        self.obstacle = {}

        self.speed_slow = 1.0

        self.tile_size = (800.0, 800.0)
        #        self.tile_scale = (0.5, 0.5)
        self.tile_scale = (1.0, 1.0, 1.0)
        pass

    def _playEnigma(self):
        self.NFS = NFSManager.getNFS(self.EnigmaName)

        #        self.object.get
        #        EnigmaScene = self.getScene()
        #        EnigmaSceneName = EnigmaScene.getName()
        #        Tiles = EnigmaScene.getSlot("Tiles")

        GameAreaLayer = SceneManager.getLayerScene("Tiles")

        EnigmaSceneName = SceneManager.getCurrentSceneName()

        self.SceneTiles = Mengine.createNode("Scene")

        MainLayerTiles = Mengine.createNode("Layer2D")
        MainLayerTiles.setMain(True)
        MainLayerTiles.setSize((1024.0, 768.0))

        self.SceneTiles.addChild(MainLayerTiles)
        self.SceneTiles.enable()

        GameAreaLayer.addChild(self.SceneTiles)

        self.CameraFollow = Mengine.createNode("RenderCameraOrthogonal")
        vp = Mengine.Viewport((0.0, 0.0), (1024.0, 768.0))
        self.CameraFollow.setOrthogonalViewport(vp)

        #        CameraFollow.setFollowTarget(Sprite_CoachEntity)
        self.CameraFollow.enable()

        self.SceneTiles.setCamera2D(self.CameraFollow)

        for tile in self.NFS.tiles:
            groupName = tile.groupName

            if Mengine.hasScene(groupName) is False:
                continue
                pass

            scene = Mengine.createScene(groupName)

            if scene is None:
                continue
                pass

            pos = (tile.x * self.tile_size[0] * self.tile_scale[0], -tile.y * self.tile_size[1] * self.tile_scale[1])

            scene.setLocalPosition(pos)
            scene.setScale(self.tile_scale)
            scene.coordinate((self.tile_size[0] * 0.5, self.tile_size[1] * 0.5))

            angle = PI * 0.5 * tile.angle
            scene.setAngle(angle)

            group = GroupManager.createGroup(groupName)

            group.onInitialize(EnigmaSceneName, scene)
            group.onActivate()
            group.onEnable()

            if group.hasObject("Interaction_PitStop") is True:
                Interaction_PitStop = group.getObject("Interaction_PitStop")
                Interaction_PitStop.setInteractive(True)

                Interaction_PitStopEntity = Interaction_PitStop.getEntity()
                Interaction_PitStopHotSpot = Interaction_PitStopEntity.getHotSpot()

                Polygon = Interaction_PitStopHotSpot.getWorldPolygon()

                PolygonPoints = Polygon.getPoints()

                self.pitstops.extend(PolygonPoints[:-1])
                pass

            barriers = []
            borders = []
            self.obstacle[(tile.x, tile.y)] = (barriers, borders)

            for i in xrange(10):
                barrierName = "Interaction_Barrier%d" % (i)

                if group.hasObject(barrierName) is False:
                    continue

                barrier = group.getObject(barrierName)

                barrier.setInteractive(True)

                barriers.append(barrier)
                pass

            for i in xrange(3):
                borderName = "Interaction_Border%d" % (i)

                if group.hasObject(borderName) is False:
                    continue

                border = group.getObject(borderName)

                border.setInteractive(True)

                borders.append(border)
                pass

            MainLayerTiles.addChild(scene)
            pass

        #        CameraFollow.velocityTo( 0.01, (0, -1), None)

        Coach = self.object.getObject("Animation_Coach")
        self.CoachEntity = Coach.getEntity()
        Coach.setRotate(-PI * 0.5)

        Socket_Coach = self.object.getObject("Socket_Coach")
        Socket_Coach.setRotate(-PI * 0.5)
        self.Socket_CoachEntity = Socket_Coach.getEntity()

        Socket_Coach.setInteractive(True)

        self.Coach = Mengine.createNode("Interender")

        Coach.setPosition((0, 0))
        self.Coach.addChild(self.CoachEntity)
        self.Coach.addChild(self.Socket_CoachEntity)

        self.Coach.setLocalPosition((400, 700))
        MainLayerTiles.addChild(self.Coach)

        self.CameraFollow.setTargetNode(self.Coach)

        self.CameraOffset = Mengine.createNode("Interender")
        self.CameraOffset.enable()
        self.CameraFollow.setTargetOffset(self.CameraOffset)
        self.CameraFollow.addChild(self.CameraOffset)

        Sprite_Progress = self.object.getObject("Sprite_Progress")

        ProgressBarStartPosition = self.ProgressBar[0]
        Sprite_Progress.setPosition(ProgressBarStartPosition)

        self.progressbar_pitstop_offset = float(self.ProgressBar[1][0] - self.ProgressBar[0][0]) / float(len(self.pitstops))

        self.setSpeed(min_speed)

        self.moveState()
        pass

    def _stopEnigma(self):
        if self.onAffectorTimingId is not None:
            Mengine.timingRemove(self.onAffectorTimingId)
            self.onAffectorTimingId = None
            pass

        if self.onCollisionTimingId is not None:
            Mengine.timingRemove(self.onCollisionTimingId)
            self.onCollisionTimingId = None
            pass
        pass

    def collideTiles(self):
        wp = self.Coach.getWorldPosition()

        coach_min = (wp.x - 50.0, wp.y - 50.0)
        coach_max = (wp.x + 50.0, wp.y + 50.0)

        collide = []

        for tile in self.NFS.tiles:
            tile_min = (tile.x * self.tile_size[0] * self.tile_scale[0], -tile.y * self.tile_size[1] * self.tile_scale[1])
            tile_max = (tile_min[0] + self.tile_size[0] * self.tile_scale[0], tile_min[1] + self.tile_size[1] * self.tile_scale[1])

            if Mengine.intersectsBoxes(coach_min, coach_max, tile_min, tile_max) is True:
                collide.append((tile.x, tile.y))
                pass
            pass

        return collide
        pass

    def moveState(self):
        self.onAffectorTimingId = Mengine.timing(0.0, self.__onAffector)
        self.onCollisionTimingId = Mengine.timing(0.5, self.__onCollision)

        self.setEventListener(onGlobalHandleMouseMove=self._onGlobalHandleMouseMove,
                              onGlobalHandleMouseButtonEvent=self._onGlobalHandleMouseButtonEvent)
        self.enableGlobalMouseEvent(True)

        if Mengine.isMouseButtonDown(0) is True:
            self.speedUp(True)
            pass
        pass

    def damageState(self):
        Mengine.removeTiming(self.onCollisionTimingId)
        self.onCollisionTimingId = None

        self.setEventListener(onGlobalHandleMouseMove=None, onGlobalHandleMouseButtonEvent=None)
        self.enableGlobalMouseEvent(False)

        #        Mengine.addInterpolatorLinearFloat(1.0, self.speed_slow, 0.0, __onSpeedZero)

        with TaskManager.createTaskChain() as tc:
            with tc.addParallelTask(2) as (tc1, tc2):
                def __onSpeedZero(value):
                    self.speed_slow = value
                    pass

                tc1.addTask("TaskInterpolatorLinearFloat", Time=1. * 1000, From=self.speed_slow, To=0.0, Fn=__onSpeedZero)
                tc2.addTask("AliasFadeIn", Time=1.0 * 1000, FadeGroupName="Fade", To=1.0)  # speed fix
                pass

            tc.addTask("TaskFunction", Fn=self.restoreStage)
            tc.addTask("TaskFunction", Fn=self.moveState)
            tc.addTask("AliasFadeOut", Time=0.5 * 1000, FadeGroupName="Fade", From=1.0)  # speed fix
            pass
        pass

    def restoreStage(self):
        Mengine.removeTiming(self.onAffectorTimingId)
        self.onAffectorTimingId = None

        self.setSpeed(min_speed)

        pitstop = self.check_pitstops[-2]
        pitstop_next = self.check_pitstops[-1]

        self.Coach.setWorldPosition(pitstop)

        dir = Mengine.direction(pitstop, pitstop_next)

        self.CoachEntity.angleStop()
        self.Socket_CoachEntity.angleStop()

        self.CoachEntity.setLocalDirection(dir)
        self.Socket_CoachEntity.setLocalDirection(dir)
        pass

    def endStage(self):
        Mengine.removeTiming(self.onCollisionTimingId)
        self.onCollisionTimingId = None

        self.enableGlobalMouseEvent(False)

        self._onWin()

        #        with TaskManager.createTaskChain(Cb = self._onWin) as tc:
        #            tc.addTask("AliasFadeIn", FadeGroupName = "Fade", To = 1.0, Time = 1.5)
        #            pass
        pass

    def _skipEnigma(self):
        self._onWin()
        pass

    def _onWin(self):
        self.enigmaComplete()
        pass

    def __onAffector(self, id, timing):
        if self.onAffectorTimingId != id:
            return

        wp = self.Coach.getWorldPosition()
        wd = self.CoachEntity.getWorldDirection()

        npx = wp.x + wd.x * self.speed * self.speed_slow * timing
        npy = wp.y + wd.y * self.speed * self.speed_slow * timing

        self.last_pos = self.Coach.getWorldPosition()

        self.Coach.setWorldPosition((npx, npy))
        pass

    def __checkPitstop(self):
        wp = self.Coach.getWorldPosition()
        sqrlength = 200.0 * 200.0
        for pitstop in self.pitstops[:]:
            if pitstop in self.check_pitstops:
                continue

            if Mengine.sqrlength_v2_v2(wp, pitstop) > sqrlength:
                continue

            self.check_pitstops.append(pitstop)

            Sprite_Progress = self.object.getObject("Sprite_Progress")

            ProgressBarX = self.ProgressBar[0][0] + self.progressbar_pitstop_offset * float(len(self.check_pitstops))

            time = 0.3
            time *= 1000  # speed fix

            TaskManager.runAlias("AliasObjectMoveTo", None, Object=Sprite_Progress,
                                 To=(ProgressBarX, self.ProgressBar[0][1]), Time=time)

            #            Sprite_Progress.setPosition((ProgressBarX, self.ProgressBar[0][1]))
            #            self.progressbar_pitstop_offset
            pass
        pass

    def __onCollision(self, id, timing):
        if self.onCollisionTimingId != id:
            return

        self.__checkPitstop()

        collides = self.collideTiles()

        last_tile = self.NFS.winTile

        #        print last_tile.x, last_tile.y, collides
        if (last_tile.x, last_tile.y) in collides:
            self.endStage()
            pass

        for collide in collides:
            barriers, borders = self.obstacle[collide]

            barrier_damage = False

            left = self.Socket_CoachEntity.getHotSpot()

            for barrier in barriers:
                barrierEntity = barrier.getEntity()
                barrierHotSpot = barrierEntity.getHotSpot()

                if Mengine.testHotspot(left, barrierHotSpot) is False:
                    continue

                barrier_damage = True
                pass

            if barrier_damage is True:
                if self.CoachSpeedDownInterpolatorId is None:
                    def __onSpeedDown(id, value, done):
                        self.speed_slow = value

                        if done is True:
                            self.CoachSpeedDownInterpolatorId = None
                            pass
                        pass

                    if self.CoachSpeedUpInterpolatorId is not None:
                        Mengine.removeTiming(self.CoachSpeedUpInterpolatorId)
                        self.CoachSpeedUpInterpolatorId = None
                        pass

                    self.CoachSpeedDownInterpolatorId = Mengine.addInterpolatorLinearFloat(1.0, self.speed_slow, 0.5, __onSpeedDown)
                    pass
            else:
                if self.CoachSpeedUpInterpolatorId is None:
                    def __onSpeedUp(id, value, done):
                        self.speed_slow = value

                        if done is True:
                            self.CoachSpeedUpInterpolatorId = None
                            pass
                        pass

                    if self.CoachSpeedDownInterpolatorId is not None:
                        Mengine.removeTiming(self.CoachSpeedDownInterpolatorId)
                        self.CoachSpeedDownInterpolatorId = None
                        pass

                    self.CoachSpeedUpInterpolatorId = Mengine.addInterpolatorLinearFloat(1.0, self.speed_slow, 1.0, __onSpeedUp)
                    pass
                pass

            border_damage = False

            for border in borders:
                borderEntity = border.getEntity()
                borderHotSpot = borderEntity.getHotSpot()

                if Mengine.testHotspot(left, borderHotSpot) is False:
                    continue

                border_damage = True
                pass

            if border_damage is True:
                self.damageState()
                break
                pass
            pass
        pass

    def _onGlobalHandleMouseMove(self, en, touchId, x, y, dx, dy):
        pos = Mengine.getCursorPosition()

        coach_pos = self.Coach.getCameraPosition(self.CameraFollow)

        dist = (pos.x - coach_pos.x, pos.y - coach_pos.y)
        dir = Mengine.norm_v2(dist)

        new_angle = Mengine.signed_angle(dir)
        coach_angel = self.CoachEntity.getAngle()

        sign_length = Mengine.angle_length(coach_angel, new_angle)

        coeff_speed = (max_speed / (self.speed + 0.001))

        angle_time = abs(sign_length) / PI * 4 * coeff_speed

        sprite_old_angle = self.CoachEntity.getAngle()
        socket_old_angle = self.Socket_CoachEntity.getAngle()

        sprite_correct_old_angle, sprite_correct_new_angle = Mengine.angle_correct_interpolate_from_to(sprite_old_angle, new_angle)
        socket_correct_old_angle, socket_correct_new_angle = Mengine.angle_correct_interpolate_from_to(socket_old_angle, new_angle)

        self.CoachEntity.setAngle(sprite_correct_old_angle)
        self.Socket_CoachEntity.setAngle(socket_correct_old_angle)

        self.CoachEntity.angleTo(angle_time, sprite_correct_new_angle, None)
        self.Socket_CoachEntity.angleTo(angle_time, socket_correct_new_angle, None)

        dist_pi_0_0 = Mengine.angle_length(sprite_correct_new_angle, PI * 0.0)
        dist_pi_0_5 = Mengine.angle_length(sprite_correct_new_angle, PI * 0.5)
        dist_pi_1_0 = Mengine.angle_length(sprite_correct_new_angle, PI * 1.0)
        dist_pi_1_5 = Mengine.angle_length(sprite_correct_new_angle, PI * 1.5)

        angle_deltha = (PI / 8)
        new_CameraState = None

        if abs(dist_pi_0_0) < angle_deltha:
            new_CameraState = "Left"
        elif abs(dist_pi_0_5) < angle_deltha:
            new_CameraState = "Up"
        elif abs(dist_pi_1_0) < angle_deltha:
            new_CameraState = "Right"
        elif abs(dist_pi_1_5) < angle_deltha:
            new_CameraState = "Down"
            pass

        if new_CameraState is not None:
            if self.CameraState != new_CameraState:
                self.CameraState = new_CameraState

                if self.CameraState == "Left":
                    self.CameraOffset.moveTo(4, (300, 0), None)
                elif self.CameraState == "Up":
                    self.CameraOffset.moveTo(4, (0, 200), None)
                elif self.CameraState == "Right":
                    self.CameraOffset.moveTo(4, (-300, 0), None)
                elif self.CameraState == "Down":
                    self.CameraOffset.moveTo(4, (0, -200), None)
                    pass
                pass
            pass

        return True
        pass

    def _onGlobalHandleMouseButtonEvent(self, en, touchId, button, isDown):
        if button != 0:
            return True
            pass

        self.speedUp(isDown)

        return True
        pass

    def setSpeed(self, value):
        self.speed = value

        animation = self.CoachEntity.getAnimatable()

        animationFactor = 1.5 + ((0.05 / self.speed) - 1) / 2.0

        animation.setAnimationFactor(animationFactor)

    def speedUp(self, isUp):
        def __onSpeedInterpolator(id, speed, done):
            self.setSpeed(speed)

            if done is True:
                self.CoachFollowInterpolatorId = None
                pass
            pass

        #        def __onCameraZoomInterpolator(id, zoom):
        #            self.CameraFollow.setScale((zoom, zoom))
        #            pass

        if isUp is True:
            if self.CoachFollowInterpolatorId is not None:
                Mengine.removeTiming(self.CoachFollowInterpolatorId)
                pass

            self.CoachFollowInterpolatorId = Mengine.addInterpolatorLinearFloat(1, self.speed, max_speed, __onSpeedInterpolator)

            #            if self.CameraFollowInterpolatorId is not None:
            #                Mengine.removeTiming(self.CameraFollowInterpolatorId)
            #                pass
            #
            #            zoom_from = self.CameraFollow.getScale().x
            #            self.CameraFollowInterpolatorId = Mengine.addInterpolatorLinearFloat(1, zoom_from, 1.2, __onCameraZoomInterpolator)
            pass

        if isUp is False:
            if self.CoachFollowInterpolatorId is not None:
                Mengine.removeTiming(self.CoachFollowInterpolatorId)
                pass

            self.CoachFollowInterpolatorId = Mengine.addInterpolatorLinearFloat(1, self.speed, min_speed, __onSpeedInterpolator)

            #            if self.CameraFollowInterpolatorId is not None:
            #                Mengine.removeTiming(self.CameraFollowInterpolatorId)
            #                pass
            #
            #            zoom_from = self.CameraFollow.getScale().x
            #            self.CameraFollowInterpolatorId = Mengine.addInterpolatorLinearFloat(1, zoom_from, 1.0, __onCameraZoomInterpolator)
            pass
        pass

    pass
