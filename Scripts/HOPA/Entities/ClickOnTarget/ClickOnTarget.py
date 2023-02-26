"""
Documentation:
https://wonderland-games.atlassian.net/wiki/spaces/HOG/pages/170754049/ClickOnTarget
"""

from Event import Event
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.ClickOnTargetManager import ClickOnTargetManager
from HOPA.EnigmaManager import EnigmaManager

Enigma = Mengine.importEntity("Enigma")

SCENE_MG_INVENTORY_GROUP = "MahjongInventory"
SCENE_COUNTER_DEMON_OBJECT = "Demon_MahjongInventory"

class Target(object):
    def __init__(self, movie_idle, movie_down, hit_movies, miss_movies, group_movie_with_target_slot, group_movie_with_target_slot_name, enigma_owner):
        self.group_movie_with_target_slot = group_movie_with_target_slot
        self.group_movie_with_target_slot_name = group_movie_with_target_slot_name

        self.enigma_owner = enigma_owner

        self.movie_idle = movie_idle
        self.movie_down = movie_down
        self.hit_movies = hit_movies
        self.miss_movies = miss_movies

        self.hit_iter = iter(hit_movies)
        self.hp = len(hit_movies)
        self.last_movie = movie_idle

        self.__setup()

        self.inventory_counter_demon = None
        self.__setupCounter()

    def __setup(self):
        slot = self.group_movie_with_target_slot.getMovieSlot(self.group_movie_with_target_slot_name)

        self.movie_down.setEnable(False)

        slot.addChild(self.movie_idle.entity.node)
        self.movie_idle.setEnable(True)
        self.movie_idle.setPlay(True)
        self.movie_idle.setLoop(True)

        for movie in self.miss_movies:
            movie.setEnable(False)

        for movie in self.hit_movies:
            slot.addChild(movie.entity.node)
            movie.setEnable(False)

    def __setupCounter(self):
        group = GroupManager.getGroup(SCENE_MG_INVENTORY_GROUP)

        if group is None:  # validate
            msg = "Enigma {} need Group {} for proper work".format(self.enigma_owner.EnigmaName, SCENE_MG_INVENTORY_GROUP)
            Trace.log("Entity", 0, msg)

        self.inventory_counter_demon = group.getObject(SCENE_COUNTER_DEMON_OBJECT)

        if self.inventory_counter_demon is None:  # validate
            msg = "Group {} should has Demon {} for proper work".format(SCENE_MG_INVENTORY_GROUP, SCENE_COUNTER_DEMON_OBJECT)
            Trace.log("Entity", 0, msg)
            return

        self.inventory_counter_demon.setParam("FoundItems", [])
        self.inventory_counter_demon.setParam("ItemsCount", len(self.hit_movies))

    def setLastMovie(self, movie):
        self.last_movie = movie

    def scopeMiss(self, source):
        if len(self.miss_movies) == 0:
            return
        rand_index = Mengine.range_rand(0, len(self.miss_movies))
        movie = self.miss_movies[rand_index]
        source.addEnable(movie)
        source.addTask("TaskMovie2Play", Movie2=movie, Wait=True)
        source.addDisable(movie)

    def scopeHit(self, source):
        self.hp -= 1

        movie_hit = next(self.hit_iter, None)
        if movie_hit is None:
            return

        if self.inventory_counter_demon is not None:  # update inventory counter
            self.inventory_counter_demon.appendParam("FoundItems", movie_hit.name)

        source.addDisable(self.last_movie)
        source.addFunction(self.setLastMovie, movie_hit)
        source.addEnable(movie_hit)
        source.addTask("TaskMovie2Play", Movie2=movie_hit, Wait=True)

        if self.hp == 0:
            source.addScope(self.scopeDown)

    def scopeDown(self, source):
        source.addDisable(self.last_movie)
        source.addEnable(self.movie_down)
        source.addTask("TaskMovie2Play", Movie2=self.movie_down)

    def cleanUp(self):
        self.movie_idle.returnToParent()

        for movie in self.hit_movies:
            movie.returnToParent()

class ClickOnTarget(Enigma):
    def __init__(self):
        super(ClickOnTarget, self).__init__()
        self.tc_main = None
        self.params = None

        # target filling
        self.filler = None
        self.target_fill = None

        self.target_fill_charged_anim = None
        self.target_fill_appear_anim = None
        self.target_fill_disappear_anim = None

        self.target_fill_slot_center = None
        self.target_fill_slot_fill_radius = None
        self.target_fill_slot_border_radius = None

        self.target_fill_affector = None

        self.b_target_fill_is_active = False

        self.f_target_fill_radius = 0.0
        self.f_target_fill_border_radius = 0.0
        self.f_filler_radius = 1.0  # const

        self.anim_timing_zero_threshold = 0.04  # const, to allow smooth filling on tick in full [0.0, 1.0] range
        self.target_filling_normalized = 0.0

        self.last_cursor_pos = None
        self.filler_mouse_pos_provider = None

        self.tc_play_target_fill_anim = None

        # target filling random movement
        self.rand_acceleration_min = 650.0  # param
        self.rand_acceleration_max = 1000.0  # param
        self.max_speed = 120.0  # param

        self.velocity = Mengine.vec2f(0.0, 0.0)
        #
        self.SemaphoreBlockClick = Semaphore(False, "ButtonClickBlock")

        self.socket_click = None
        self.socket_click_event = Event("onSocketClick")

        # visual target
        self.target = None

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def loadParam(self):
        self.params = ClickOnTargetManager.getParam(self.EnigmaName)

    def __checkMovieSlotExists(self, movie, slot_name):
        if not movie.entity.hasMovieSlot(slot_name):
            msg = "Enigma {}: Movie {} should has slot with name: {}".format(self.EnigmaName, movie.name, slot_name)
            Trace.log("Entity", 0, msg)

    def setup(self):
        # cteate socket click
        scene = SceneManager.getCurrentScene()
        layer = scene.getMainLayer()
        self.socket_click = layer.createChild("HotSpotPolygon")
        self.socket_click.setPolygon([(0, 0), (1280, 0), (1280, 768), (0, 768)])
        self.socket_click.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        self.socket_click.enable()

        # initialize filler
        self.filler = self.object.getObject(self.params.filler)

        self.rand_acceleration_min = self.params.filler_rand_accel_min
        self.rand_acceleration_max = self.params.filler_rand_accel_max
        self.max_speed = self.params.filler_max_speed

        # initialize target fill
        self.target_fill = self.object.getObject(self.params.target_fill)

        self.__checkMovieSlotExists(self.target_fill, "center")
        self.target_fill_slot_center = self.target_fill.getMovieSlot("center")

        self.__checkMovieSlotExists(self.target_fill, "fill_radius")
        self.target_fill_slot_fill_radius = self.target_fill.getMovieSlot("fill_radius")

        self.__checkMovieSlotExists(self.target_fill, "border_radius")
        self.target_fill_slot_border_radius = self.target_fill.getMovieSlot("border_radius")

        # initialize target fill animations
        self.target_fill_charged_anim = self.object.getObject(self.params.target_charge_anim)
        self.target_fill_charged_anim.setEnable(False)
        self.__checkMovieSlotExists(self.target_fill_charged_anim, "target")

        self.target_fill_appear_anim = self.object.getObject(self.params.target_appear_anim)
        self.target_fill_appear_anim.setEnable(False)
        self.__checkMovieSlotExists(self.target_fill_appear_anim, "target")

        self.target_fill_disappear_anim = self.object.getObject(self.params.target_disappear_anim)
        self.target_fill_disappear_anim.setEnable(False)
        self.__checkMovieSlotExists(self.target_fill_appear_anim, "target")

        # initialize target in mg group
        group_name = EnigmaManager.getEnigmaGroupName(self.EnigmaName)  # Movie on scene with target slot
        group = GroupManager.getGroup(group_name)
        group_movie_with_target_slot = group.getObject(self.params.movie_in_group_with_target_mg_slot)

        if group_movie_with_target_slot is None:  # validate
            msg = "Group {} of Enigma {} should had Movie: {}".format(group_name, self.__class__.__name__, self.params.movie_in_group_with_target_mg_slot)
            Trace.log("Entity", 0, msg)

        self.__checkMovieSlotExists(group_movie_with_target_slot, "target_mg")

        target_idle = self.object.getObject(self.params.target_idle)
        target_down = self.object.getObject(self.params.target_down)
        target_hit_list = [self.object.getObject(hit_movie) for hit_movie in self.params.target_hit_list]
        target_miss_list = [self.object.getObject(miss_movie) for miss_movie in self.params.target_miss_list]

        self.target = Target(target_idle, target_down, target_hit_list, target_miss_list, group_movie_with_target_slot, "target_mg", self)

    def activate(self):
        # add filler as target fill child
        filler_en = self.filler.getEntityNode()
        self.target_fill.entity.addChild(self.filler.entity.node)

        # initialize filler start location
        target_fill_local_center = self.target_fill_slot_center.getWorldPosition()
        filler_en.setLocalPosition(target_fill_local_center)

        # initialize target fill radius with slots
        self.f_target_fill_radius = Mengine.length_v2_v2(self.target_fill_slot_center.getWorldPosition(), self.target_fill_slot_fill_radius.getWorldPosition())

        # initialize target border radius with slots
        self.f_target_fill_border_radius = Mengine.length_v2_v2(self.target_fill_slot_center.getWorldPosition(), self.target_fill_slot_border_radius.getWorldPosition())

        # set target appear anim on start
        self.target_fill_appear_anim.setLastFrame(False)
        self.target_fill_appear_anim.setEnable(True)
        self.target_fill_appear_anim.setPlay(False)
        target_slot = self.target_fill_appear_anim.getMovieSlot("target")
        target_slot.addChild(self.target_fill.entity.node)

        # run filler move on cursor
        self.filler_mouse_pos_provider = Mengine.addMousePositionProvider(None, None, None, self.moveFillerOnCursorChangePos)

        # run target fill tick affector logic handler
        self.target_fill_affector = Mengine.addAffector(self.targetFillingAffector)

    def cleanUp(self):
        if self.tc_main is not None:
            self.tc_main.cancel()
            self.tc_main = None

        if self.target is not None:
            self.target.cleanUp()
            self.target = None

        if self.filler is not None:
            self.filler.returnToParent()

        if self.target_fill is not None:
            self.target_fill.returnToParent()

        if self.target_fill_affector is not None:
            Mengine.removeAffector(self.target_fill_affector)
            self.target_fill_affector = None

        if self.filler_mouse_pos_provider is not None:
            Mengine.removeMousePositionProvider(self.filler_mouse_pos_provider)
            self.filler_mouse_pos_provider = None

        if self.tc_play_target_fill_anim is not None:
            self.tc_play_target_fill_anim.cancel()
            self.tc_play_target_fill_anim = None

        arrow_node = Mengine.getArrow().node  # force cursor alpha back to 1.0
        arrow_node.getRender().setLocalAlpha(1.0)

        self.setTargetFillActive(False)  # force disable block socket

        Mengine.destroyNode(self.socket_click)

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def moveFillerOnCursorChangePos(self, _touchID, pos):
        if not self.b_target_fill_is_active:
            self.last_cursor_pos = None
            return

        if self.last_cursor_pos is None:  # initialize cursor direction
            self.last_cursor_pos = pos
            return

        # update filler pos
        delta_pos = pos - self.last_cursor_pos

        filler_pos = self.filler.entity.node.getWorldPosition()
        filler_pos += delta_pos

        if self.isFillerInBorderRadius(filler_pos):
            self.filler.entity.node.setWorldPosition(filler_pos)

        self.last_cursor_pos = pos

    def isFillerInBorderRadius(self, filler_pos):
        """
        simple collision detection
        https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
        """

        target_pos = self.target_fill_slot_center.getWorldPosition()

        dx = target_pos.x - filler_pos.x
        dy = target_pos.y - filler_pos.y

        distance = Mengine.sqrtf(dx * dx + dy * dy)

        return distance < self.f_target_fill_border_radius + self.f_filler_radius

    def isFillerInFillRadius(self):
        """
        simple collision detection
        https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
        """

        filler_pos = self.filler.entity.node.getWorldPosition()
        target_pos = self.target_fill_slot_center.getWorldPosition()

        dx = target_pos.x - filler_pos.x
        dy = target_pos.y - filler_pos.y

        distance = Mengine.sqrtf(dx * dx + dy * dy)

        return distance < self.f_target_fill_radius + self.f_filler_radius

    def updateTargetFilling(self, delta_time, b_fill_positive):
        anim_duration = self.target_fill.entity.getDuration() / 1000
        anim_timing_delta = delta_time / anim_duration
        anim_timing_normalized = self.target_filling_normalized

        if b_fill_positive:
            anim_timing_normalized += anim_timing_delta

            if anim_timing_normalized >= 1.0 - self.anim_timing_zero_threshold:  # clamp
                anim_timing_normalized = 1.0

        else:
            anim_timing_normalized -= anim_timing_delta

            if anim_timing_normalized <= self.anim_timing_zero_threshold:  # clamp
                anim_timing_normalized = 0.0

        self.target_filling_normalized = anim_timing_normalized

        self.target_fill.setTimingProportion(anim_timing_normalized)

    def computeFillerRandMove(self, delta_time):
        """compute velocity:
        v = v0 + a*t

        compute movement delta:
        Velocity Verlet integration (http://en.wikipedia.org/wiki/Verlet_integration#Velocity_Verlet)
        p = p0 + v0*t + 1/2*a*t^2
        p = p0 + v0*t + 1/2*((v1-v0)/t)*t^2
        p = p0 + v0*t + 1/2*((v1-v0))*t
        """

        delta_sec = delta_time / 1000.0

        pos = self.filler.entity.node.getWorldPosition()

        if self.isFillerInBorderRadius(pos):
            # random acceleration:
            accel_size = Mengine.randf(self.rand_acceleration_max - self.rand_acceleration_min) + self.rand_acceleration_min
            rand_x = (Mengine.randf(1.0) * 2.0 - 1.0) * accel_size  # range: [-accel_size; accel_size]

            accel_size = Mengine.sqrtf(accel_size * accel_size - rand_x * rand_x)
            rand_y = (Mengine.randf(1.0) * 2.0 - 1.0) * accel_size  # range: [-accel_size; accel_size]

            rand_accel = Mengine.vec2f(rand_x, rand_y)

            velocity_delta = rand_accel * delta_sec * 0.5

        else:
            # try to stay in target fill border, accelerate to target_fill center:
            direction = self.target_fill_slot_center.getWorldPosition() - pos
            direction_size = Mengine.length_v2(direction)
            direction.x, direction.y = direction.x / direction_size, direction.y / direction_size  # normalize

            velocity_delta = direction * (self.rand_acceleration_min * delta_sec * 0.5)

        # compute velocity:
        self.velocity += velocity_delta

        # limit velocity:
        velocity_size = Mengine.length_v2(self.velocity)
        if velocity_size > self.max_speed:
            self.velocity.x = self.max_speed * self.velocity.x / velocity_size
            self.velocity.y = self.max_speed * self.velocity.y / velocity_size

        # update position:
        pos += self.velocity * delta_sec
        self.filler.entity.node.setWorldPosition(pos)

    def targetFillingAffector(self, delta_time):
        if not self.b_target_fill_is_active:
            return False

        self.computeFillerRandMove(delta_time)

        b_fill_target_positive = self.isFillerInFillRadius()
        self.updateTargetFilling(delta_time, b_fill_target_positive)

        b_enable_charged_anim = self.target_filling_normalized == 1.0
        self.enableTargetFillChargedAnim(b_enable_charged_anim)

        return False

    def enableTargetFillChargedAnim(self, b_enable):
        target_fill_en = self.target_fill.getEntityNode()

        if b_enable:
            target_charged_slot = self.target_fill_charged_anim.getMovieSlot("target")

            if target_fill_en.getParent() == target_charged_slot:  # check parent
                return

            target_charged_slot.addChild(target_fill_en)

            if self.target_fill_appear_anim.getEnable():
                self.target_fill_appear_anim.setEnable(False)

            self.target_fill_charged_anim.setEnable(True)
            self.target_fill_charged_anim.setPlay(True)
            self.target_fill_charged_anim.setLoop(True)

        else:
            target_appear_slot = self.target_fill_appear_anim.getMovieSlot("target")

            if target_fill_en.getParent() == target_appear_slot:  # check parent
                return

            target_appear_slot.addChild(target_fill_en)

            if self.target_fill_charged_anim.getEnable():
                self.target_fill_charged_anim.setEnable(False)

            self.target_fill_appear_anim.setEnable(True)
            self.target_fill_appear_anim.setLastFrame(True)

    def playTargetFillAppearAnim(self):
        if self.tc_play_target_fill_anim is not None and self.tc_play_target_fill_anim.state is self.tc_play_target_fill_anim.RUN:
            return

        target_appear_slot = self.target_fill_appear_anim.getMovieSlot("target")
        target_fill_en = self.target_fill.getEntityNode()

        if target_fill_en.getParent() != target_appear_slot:  # check parent
            target_appear_slot.addChild(target_fill_en)

        self.target_filling_normalized = 0.0  # drop target filling
        self.target_fill.setTimingProportion(self.target_filling_normalized)

        self.filler.entity.node.setLocalPosition((0.0, 0.0))  # reset filler position
        self.velocity = Mengine.vec2f(0.0, 0.0)  # reset filler velocity

        if self.target_fill_disappear_anim.getEnable():
            self.target_fill_disappear_anim.setEnable(False)

        self.target_fill_appear_anim.setLastFrame(False)
        self.target_fill_appear_anim.setEnable(True)
        self.target_fill_appear_anim.setPlay(False)

        arrow_node = Mengine.getArrow().node
        arrow_alpha_time = self.target_fill_appear_anim.entity.getDuration() / 1000

        # tc
        if self.tc_play_target_fill_anim is not None:
            self.tc_play_target_fill_anim.cancel()

        self.tc_play_target_fill_anim = TaskManager.createTaskChain()
        with self.tc_play_target_fill_anim as tc:
            with tc.addParallelTask(2) as (parallel_0, parallel_1):
                parallel_0.addTask("TaskNodeAlphaTo", Node=arrow_node, Time=arrow_alpha_time, To=0.0)
                parallel_1.addPlay(self.target_fill_appear_anim, Wait=True)

            tc.addFunction(self.setTargetFillActive, True)
            tc.addSemaphore(self.SemaphoreBlockClick, To=False)

    def playTargetFillDisappearAnim(self):
        if self.tc_play_target_fill_anim is not None and self.tc_play_target_fill_anim.state is self.tc_play_target_fill_anim.RUN:
            return

        self.setTargetFillActive(False)

        target_disappear_slot = self.target_fill_disappear_anim.getMovieSlot("target")
        target_fill_en = self.target_fill.getEntityNode()

        if target_fill_en.getParent() != target_disappear_slot:  # check parent
            target_disappear_slot.addChild(target_fill_en)

        if self.target_fill_charged_anim.getEnable():
            self.target_fill_charged_anim.setEnable(False)

        if self.target_fill_appear_anim.getEnable():
            self.target_fill_appear_anim.setEnable(False)

        self.target_fill_disappear_anim.setLastFrame(False)
        self.target_fill_disappear_anim.setPlay(False)
        self.target_fill_disappear_anim.setEnable(True)

        arrow_node = Mengine.getArrow().node
        arrow_alpha_time = self.target_fill_disappear_anim.entity.getDuration() / 1000
        # tc
        if self.tc_play_target_fill_anim is not None:
            self.tc_play_target_fill_anim.cancel()

        self.tc_play_target_fill_anim = TaskManager.createTaskChain()
        with self.tc_play_target_fill_anim as tc:
            with tc.addParallelTask(2) as (parallel_0, parallel_1):
                parallel_0.addTask("TaskNodeAlphaTo", Node=arrow_node, Time=arrow_alpha_time, To=1.0)
                parallel_1.addPlay(self.target_fill_disappear_anim, Wait=True)

            if self.target_filling_normalized == 1.0:
                tc.addScope(self.target.scopeHit)
            else:
                tc.addScope(self.target.scopeMiss)

            tc.addSemaphore(self.SemaphoreBlockClick, To=False)

            with tc.addIfTask(lambda: self.target.hp == 0) as (true, _):
                true.addFunction(self.enigmaComplete)

    def setTargetFillActive(self, b_is_active):
        if self.b_target_fill_is_active != b_is_active:
            GuardBlockInput.enableBlockSocket(b_is_active)

        self.b_target_fill_is_active = b_is_active

    def onMouseClick(self):
        if self.b_target_fill_is_active:
            self.playTargetFillDisappearAnim()
        else:
            self.playTargetFillAppearAnim()

    def _onMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button != 0:
            return False

        self.socket_click_event()
        return False

    def toolbarButtonsBlock(self, state):
        if GroupManager.hasGroup("Toolbar"):
            if GroupManager.hasObject("Toolbar", "Movie2Button_Menu"):
                movie2_button_menu = GroupManager.getObject("Toolbar", "Movie2Button_Menu")
                movie2_button_menu.setBlock(state)

        if DemonManager.hasDemon("SkipPuzzle"):
            demon_hint = DemonManager.getDemon("SkipPuzzle")
            if demon_hint.hasObject("Movie2Button_Skip"):
                movie2_button_hint = demon_hint.getObject("Movie2Button_Skip")
                movie2_button_hint.setBlock(state)

        if GroupManager.hasGroup("OpenMap"):
            if GroupManager.hasObject("OpenMap", "Movie2Button_Map"):
                movie2_button_map = GroupManager.getObject("OpenMap", "Movie2Button_Map")
                movie2_button_map.setBlock(state)

        if GroupManager.hasGroup("Open_Journal"):
            if GroupManager.hasObject("Open_Journal", "Movie2Button_Journal"):
                movie2_button_journal = GroupManager.getObject("Open_Journal", "Movie2Button_Journal")
                movie2_button_journal.setBlock(state)

        if GroupManager.hasGroup("OpenTask"):
            if GroupManager.hasObject("OpenTask", "Movie2Button_OpenTask"):
                movie2_button_task = GroupManager.getObject("OpenTask", "Movie2Button_OpenTask")
                movie2_button_task.setBlock(state)

        if GroupManager.hasGroup("InventoryLock"):
            if GroupManager.hasObject("InventoryLock", "Movie2CheckBox_Lock"):
                movie2_button_hide_inventory = GroupManager.getObject("InventoryLock", "Movie2CheckBox_Lock")
                movie2_button_hide_inventory_entity = movie2_button_hide_inventory.getEntity()
                movie2_button_hide_inventory_entity.setBlock(state)

    def __filterClick(self, value):
        self.SemaphoreBlockClick.setValue(value)

        return True

    def runTaskChains(self):
        if self.tc_main is not None:
            self.tc_main.cancel()

        self.tc_main = TaskManager.createTaskChain(Repeat=True)
        with self.tc_main as tc_click:
            tc_click.addSemaphore(self.SemaphoreBlockClick, From=False)
            tc_click.addSemaphore(self.SemaphoreBlockClick, To=True)
            tc_click.addEvent(self.socket_click_event)
            tc_click.addFunction(self.toolbarButtonsBlock, True)
            tc_click.addFunction(self.onMouseClick)

            tc_click.addSemaphore(self.SemaphoreBlockClick, From=False)
            tc_click.addSemaphore(self.SemaphoreBlockClick, To=True)
            tc_click.addTask("TaskMouseButtonClick", isDown=True)
            tc_click.addFunction(self.onMouseClick)
            tc_click.addFunction(self.toolbarButtonsBlock, False)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ClickOnTarget, self)._onPreparation()
        self.loadParam()
        self.setup()

    def _onActivate(self):
        super(ClickOnTarget, self)._onActivate()
        self.activate()

    def _onDeactivate(self):
        super(ClickOnTarget, self)._onDeactivate()
        self.cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.runTaskChains()

    def _stopEnigma(self):
        if self.tc_main is not None:
            self.tc_main.cancel()

    def _restoreEnigma(self):
        self.runTaskChains()

    def _resetEnigma(self):
        self.cleanUp()
        self.setup()
        self.activate()
        self.runTaskChains()

    def _skipEnigmaScope(self, skip_source):
        self.tc_main.cancel()

        def scopeDisableTargetFill(source):
            self.setTargetFillActive(False)

            if self.tc_play_target_fill_anim is not None:
                self.tc_play_target_fill_anim.cancel()

            target_disappear_slot = self.target_fill_disappear_anim.getMovieSlot("target")
            target_fill_en = self.target_fill.getEntityNode()

            b_is_charged_anim_active = self.target_fill_charged_anim.getEnable()
            if b_is_charged_anim_active:
                self.target_fill_charged_anim.setEnable(False)

            b_is_appear_anim_active = self.target_fill_appear_anim.getEnable()
            if b_is_appear_anim_active:
                self.target_fill_appear_anim.setEnable(False)

            if b_is_appear_anim_active or b_is_appear_anim_active:
                if target_fill_en.getParent() != target_disappear_slot:  # check parent
                    target_disappear_slot.addChild(target_fill_en)

                self.target_fill_disappear_anim.setLastFrame(False)
                self.target_fill_disappear_anim.setPlay(False)
                self.target_fill_disappear_anim.setEnable(True)

                arrow_node = Mengine.getArrow().node
                arrow_alpha_time = self.target_fill_disappear_anim.entity.getDuration() / 1000

                with source.addParallelTask(2) as (parallel_0, parallel_1):
                    parallel_0.addTask("TaskNodeAlphaTo", Node=arrow_node, Time=arrow_alpha_time, To=1.0)
                    parallel_1.addPlay(self.target_fill_disappear_anim)

        skip_source.addDelay(self.target_fill_disappear_anim.entity.getDuration() / 1000)
        skip_source.addScope(scopeDisableTargetFill)

        for _ in range(self.target.hp):
            skip_source.addScope(self.target.scopeHit)