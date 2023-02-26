from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.Hunt2dManager import Hunt2dManager

Enigma = Mengine.importEntity("Enigma")

class Weapon(object):
    def __init__(self, movie_weapon_in_attack, movie_weapon_shot_effect, movie_weapon_in_hand, movie_weapon_start):
        self.movie_weapon_in_attack = movie_weapon_in_attack
        self.movie_weapon_shot_effect = movie_weapon_shot_effect
        self.movie_weapon_in_hand = movie_weapon_in_hand
        self.movie_weapon_start = movie_weapon_start

        self.movie_weapon_in_attack.setEnable(False)
        self.movie_weapon_shot_effect.setEnable(False)
        self.movie_weapon_start.setEnable(False)

    def cleanUp(self):
        for movie in [self.movie_weapon_shot_effect, self.movie_weapon_in_hand, self.movie_weapon_start]:
            if movie is None:
                continue
            movie.getEntityNode().removeFromParent()

class HuntersHand(object):
    def __init__(self, movie_hunters_hand, movie_hunters_hand_hide, weapon):
        self.movie_hunters_hand = movie_hunters_hand
        self.movie_hunters_hand_hide = movie_hunters_hand_hide
        self.weapon = weapon
        self.left_border = movie_hunters_hand.getMovieSlot('left_border').getWorldPosition().x
        self.right_border = movie_hunters_hand.getMovieSlot('right_border').getWorldPosition().x
        self.sight = movie_hunters_hand.getMovieSlot('sight')
        self.activity_area_length = self.right_border - self.left_border

        self.movie_hunters_hand_hide.setEnable(False)
        self.__setWeaponOnHand()

    def scopePlayHideAnimation(self, source):
        source.addPlay(self.movie_hunters_hand, Wait=True, Loop=False)
        source.addDisable(self.movie_hunters_hand)

        source.addEnable(self.movie_hunters_hand_hide)
        source.addPlay(self.movie_hunters_hand_hide, Wait=True, Loop=False)

    def __setWeaponOnHand(self):
        slot = self.movie_hunters_hand.getMovieSlot('weapon')

        slot.addChild(self.weapon.movie_weapon_shot_effect.getEntityNode())
        slot.addChild(self.weapon.movie_weapon_in_hand.getEntityNode())
        slot.addChild(self.weapon.movie_weapon_start.getEntityNode())

    def getSightPosition(self):
        return self.sight.getWorldPosition()

    def prepareToShot(self, source):
        sight_position = self.getSightPosition()
        movie_weapon_in_attack_entity_node = self.weapon.movie_weapon_in_attack.getEntityNode()

        source.addFunction(movie_weapon_in_attack_entity_node.setWorldPosition, sight_position)
        source.addEnable(self.weapon.movie_weapon_in_attack)

class Prey(object):
    def __init__(self, movie_prey_body_box, movie_prey_idle_left, movie_prey_idle_right, movie_prey_death, movie_prey_run_to_right_side, movie_prey_run_to_left_side, movie_prey_turned_to_right_side, movie_prey_turned_to_left_side, alpha_time):
        self.movie_prey_body_box = movie_prey_body_box
        self.movie_prey_idle_left = movie_prey_idle_left
        self.movie_prey_idle_right = movie_prey_idle_right
        self.movie_prey_death = movie_prey_death

        self.movie_prey_run_to_right_side = movie_prey_run_to_right_side
        self.movie_prey_run_to_left_side = movie_prey_run_to_left_side

        self.movie_prey_turned_to_right_side = movie_prey_turned_to_right_side
        self.movie_prey_turned_to_left_side = movie_prey_turned_to_left_side

        self.side = None

        self.entity_node = movie_prey_body_box.getEntityNode()
        self.socket = self.movie_prey_body_box.getSocket('body_box')

        self.alpha_time = alpha_time  # todo: add to enigma xls

        self.movie_prey_death.setEnable(False)

        self.modes_sides = {('run', 'right'): self.movie_prey_run_to_right_side, ('run', 'left'): self.movie_prey_run_to_left_side, ('idle', 'right'): self.movie_prey_idle_right, ('idle', 'left'): self.movie_prey_idle_left, }

    def cleanUp(self):
        for movie in [self.movie_prey_idle_left, self.movie_prey_idle_right, self.movie_prey_run_to_right_side, self.movie_prey_run_to_left_side, self.movie_prey_turned_to_right_side, self.movie_prey_turned_to_left_side]:
            if movie is None:
                continue
            movie.getEntityNode().removeFromParent()

    def setSide(self, value):
        self.side = value

    def getSide(self):
        return self.side

    def scopeAlphaTo(self, source, mode, turn_on):
        """ Scope for disable/enable states with alphaTo

        :param source:
        :param mode: run or idle
        :param turn_on: True for enable, False for disable
        :return:
        """
        # assert self.modes_sides.get(('idle', 'right'), None) == self.movie_prey_idle_right
        side = self.getSide()

        obj = self.modes_sides.get((mode, side), None)
        if obj is None:
            # Trace.log("Manager", 0, "self.modes_sides not has key ({}, {})".format(mode, side))
            return

        from_ = 0.0 if turn_on is True else 1.0
        to_ = 1.0 if turn_on is True else 0.0

        source.addTask("AliasObjectAlphaTo", Object=obj, From=from_, To=to_, Time=self.alpha_time)

    def disableRunMode(self):
        """ This method enable run animation to side and enable Idle state

        :return: True if run mode has been disabled, False if obj don`t support run mode and run mode don`t disabled
        """

        self.movie_prey_run_to_right_side.setEnable(False)
        self.movie_prey_run_to_left_side.setEnable(False)
        self.setSide(None)

        return True

    def enableRunMode(self, side):
        """ This method enable run animation to side, disable Idle state

        :param side: left or right
        :return: True if run mode enable, False if animation don`t exists and mode don`t enable
        """

        self.setSide(side)

        if side == 'right':
            self.movie_prey_run_to_right_side.setEnable(True)
            self.movie_prey_run_to_left_side.setEnable(False)
            return True

        if side == 'left':
            self.movie_prey_run_to_right_side.setEnable(False)
            self.movie_prey_run_to_left_side.setEnable(True)
            return True
        return False

    def setIdleState(self, side):
        """ This method disable run mode movie, play change state movie and enable idle state movie

        :return:
        """

        if side == 'right':
            idle_state = self.movie_prey_idle_right
        else:
            idle_state = self.movie_prey_idle_left

        idle_state.setEnable(True)
        self.setSide(side)

    def disableIdleState(self):
        """ This method disable idle state movies

        :return:
        """
        self.movie_prey_idle_left.setEnable(False)
        self.movie_prey_idle_right.setEnable(False)
        self.setSide(None)

    def scopeTurnedTo(self, source, side):
        """ This method disable idle state movie, play change state movie and enable run mode movie

        :param source:
        :param side: left or right
        :return:
        """

        current_side = self.getSide()
        if current_side is None or current_side == side:
            source.addDummy()
            return

        if current_side == 'left':
            rotate_movie = self.movie_prey_turned_to_right_side
        else:
            rotate_movie = self.movie_prey_turned_to_left_side

        source.addEnable(rotate_movie)
        source.addPlay(rotate_movie, Wait=True)
        source.addDisable(rotate_movie)

    def scopePlayDeathAnimation(self, source):
        source.addDisable(self.movie_prey_body_box)
        source.addFunction(self.movie_prey_death.getEntityNode().setWorldPosition, self.getPosition())
        source.addEnable(self.movie_prey_death)

        source.addPlay(self.movie_prey_death, Loop=False, Wait=True)

        source.addDisable(self.movie_prey_death)

    def checkHit(self, shot_point_wp):
        """ This method check hunter`s hit

        check that the socket includes the coordinates of shot_point
        this can be done using the method pickHotspot, but position must be in resolution section

        :param shot_point_wp: in WorldPosition
        :return: True if hit is success
        """

        screen_position = Mengine.fromWorldToScreenPosition((shot_point_wp[0], shot_point_wp[1], 0.0))
        hotspots_names = Mengine.pickAllHotspot(screen_position)

        return self.socket in hotspots_names

    def getPosition(self):
        return self.entity_node.getWorldPosition()

    def setPosition(self, position):
        self.entity_node.setWorldPosition(position)

class PreysTrace(object):
    """
    This module save and randomize next trace point, trace, speed and delay on trace point
    """
    def __init__(self, movie_content, params):
        number_race_points = params.trace_points_number

        self.prey_trace_points = {}
        for i in range(number_race_points):
            self.prey_trace_points[i] = movie_content.getMovieSlot('prey_track_point_{}'.format(i))

        self.current_trace_point = None
        self.finish_trace_point = None
        self.trace_speed = None
        self.semaphore_trace_end = Semaphore(False, "PreysTraceEnd")

        self.static_trace_rout = params.trace
        if len(self.static_trace_rout) == 0:
            self.static_trace_rout = None
        self.static_trace_rout_index = 0

        self.preys_move_speed_default_value_name = params.preys_move_speed_default_value
        self.delay_on_finish_trace_point_default_value_name = params.delay_on_finish_trace_point_default_value

    def checkTraceEnd(self):
        """ Check finish current trace by prey

        :return: True if prey is in finish trace point, else False
        """
        if self.current_trace_point != self.finish_trace_point:
            return False

        self.semaphore_trace_end.setValue(True)
        return True

    def createNewTrace(self):
        """ This method create with randomize new trace from current trace point

        :return: finish_trace_point
        """
        self.trace_speed = self.__getNewTraceSpeed()

        trace_points_indexes = self.prey_trace_points.keys()
        trace_points_indexes.remove(self.current_trace_point)

        if self.static_trace_rout is None:
            finish_trace_point_index = Mengine.rand(len(trace_points_indexes))
            self.finish_trace_point = trace_points_indexes[finish_trace_point_index]
        else:
            self.finish_trace_point = self.static_trace_rout[self.static_trace_rout_index]
            self.static_trace_rout_index = (self.static_trace_rout_index + 1) % len(self.static_trace_rout)

        return self.finish_trace_point

    def setCurrentTextPoint(self, value):
        self.current_trace_point = value

    def getNextTracePointIndex(self):
        """ This method return next trace point from trace to finish

        :return: next trace point
        """
        if self.current_trace_point > self.finish_trace_point:
            return self.current_trace_point - 1
        elif self.current_trace_point < self.finish_trace_point:
            return self.current_trace_point + 1

        Trace.log("Entity", 0, "current_trace_point == finish_trace_point")

    def getNextTracePoint(self):
        return self.getTracePoint(self.getNextTracePointIndex())

    def getCurrentTracePoinIndex(self):
        return self.current_trace_point

    def getCurrentTracePoint(self):
        return self.getTracePoint(self.getCurrentTracePoinIndex())

    def getTracePoint(self, index):
        return self.prey_trace_points.get(index, None)

    def getTracePointPosition(self, index):
        return self.getTracePoint(index).getWorldPosition()

    def __getNewTraceSpeed(self):
        """ This method randomize prey`s speed

        :return: new prey`s speed
        """
        tuple_speed_borders = DefaultManager.getDefaultTuple(self.preys_move_speed_default_value_name, (0.1, 0.5))
        return float(Mengine.range_rand(tuple_speed_borders[0] * 100, tuple_speed_borders[1] * 100)) / 100

    def getFinishDelay(self):
        """ This method randomize prey`s delay on finish trace_point

        :return: delay in ms
        """
        tuple_delay_borders = DefaultManager.getDefaultTuple(self.delay_on_finish_trace_point_default_value_name, (1000, 3000))

        return Mengine.range_rand(tuple_delay_borders[0], tuple_delay_borders[1])

class Hunt2d(Enigma):
    def __init__(self):
        super(Hunt2d, self).__init__()
        self.tc_hunter = None
        self.tc_prey = None
        self.hunters_hand = None
        self.prey = None
        self.movie_content = None
        self.preys_trace = None
        self.params = None

        self.tc_first_launch = None

    def _onPreparation(self):
        super(Hunt2d, self)._onPreparation()
        self.__loadParam()
        self.__setupArt()
        self.semaphore_resolve_shot = Semaphore('Hunt2dResolveShot', False)
        self.mouse_position_provider = Mengine.addMousePositionProvider(None, None, None, self.__cbUpdateMousePositionProvider)

    def __cbUpdateMousePositionProvider(self, _, position):
        if self.semaphore_resolve_shot.getValue() is True:
            return
        self.__updateHuntersHand(position.x)

    def __updateHuntersHand(self, mouse_x):
        """ This method set timing hunters_hand movie depending on the cursor position on activity_area_length

        :param mouse_x: mouse`s x coordinate
        :return:
        """
        if mouse_x > self.hunters_hand.left_border and (mouse_x < self.hunters_hand.right_border):
            percent = (mouse_x - self.hunters_hand.left_border) / self.hunters_hand.activity_area_length
            self.hunters_hand.movie_hunters_hand.setTimingProportion(percent)
        elif mouse_x <= self.hunters_hand.left_border:
            self.hunters_hand.movie_hunters_hand.setTimingProportion(0)
        elif mouse_x >= self.hunters_hand.right_border:
            self.hunters_hand.movie_hunters_hand.setTimingProportion(1)

    def __loadParam(self):
        self.params = Hunt2dManager.getParam(self.EnigmaName)

    def __setupArt(self):
        group = self.object
        if GroupManager.hasGroup(self.params.group_name) is True:
            group = GroupManager.getGroup(self.params.group_name)

        self.movie_content = group.getObject('Movie2_Content')

        movie_hunters_hand_hide = group.getObject('Movie2_HuntersHandHide')
        movie_hunters_hand = group.getObject('Movie2_HuntersHand')
        movie_weapon_in_attack = group.getObject('Movie2_WeaponInAttack')
        movie_weapon_shot_effect = group.getObject('Movie2_WeaponBangEffect')
        movie_weapon_start = group.getObject('Movie2_WeaponStart')
        movie_weapon_in_hand = group.getObject('Movie2_WeaponInHand')

        movie_prey_body_box = group.getObject('Movie2_PreyBodyBox')
        body_box_en = movie_prey_body_box.getEntityNode()

        movie_prey_death = group.getObject('Movie2_PreyDeath')

        movie_prey_idle_left = group.getObject('Movie2_PreyIdleLeft')
        body_box_en.addChild(movie_prey_idle_left.getEntityNode())
        movie_prey_idle_left.setLoop(True)
        movie_prey_idle_left.setPlay(True)
        movie_prey_idle_left.setEnable(False)

        movie_prey_idle_right = group.getObject('Movie2_PreyIdleRight')
        body_box_en.addChild(movie_prey_idle_right.getEntityNode())
        movie_prey_idle_right.setLoop(True)
        movie_prey_idle_right.setPlay(True)
        movie_prey_idle_right.setEnable(False)

        movie_prey_run_to_right_side = group.getObject('Movie2_PreyRunToRightSide')
        body_box_en.addChild(movie_prey_run_to_right_side.getEntityNode())
        movie_prey_run_to_right_side.setLoop(True)
        movie_prey_run_to_right_side.setPlay(True)
        movie_prey_run_to_right_side.setEnable(False)

        movie_prey_run_to_left_side = group.getObject('Movie2_PreyRunToLeftSide')
        body_box_en.addChild(movie_prey_run_to_left_side.getEntityNode())
        movie_prey_run_to_left_side.setLoop(True)
        movie_prey_run_to_left_side.setPlay(True)
        movie_prey_run_to_left_side.setEnable(False)

        movie_prey_turned_to_right_side = group.getObject('Movie2_PreyTurnedToRightSide')
        body_box_en.addChild(movie_prey_turned_to_right_side.getEntityNode())
        movie_prey_turned_to_right_side.setEnable(False)

        movie_prey_turned_to_left_side = group.getObject('Movie2_PreyTurnedToLeftSide')
        body_box_en.addChild(movie_prey_turned_to_left_side.getEntityNode())
        movie_prey_turned_to_left_side.setEnable(False)

        weapon = Weapon(movie_weapon_in_attack, movie_weapon_shot_effect, movie_weapon_in_hand, movie_weapon_start)

        movie_weapon_in_hand.setPlay(True)
        movie_weapon_in_hand.setLoop(True)

        self.hunters_hand = HuntersHand(movie_hunters_hand, movie_hunters_hand_hide, weapon)

        self.prey = Prey(movie_prey_body_box, movie_prey_idle_left, movie_prey_idle_right, movie_prey_death, movie_prey_run_to_right_side, movie_prey_run_to_left_side, movie_prey_turned_to_right_side, movie_prey_turned_to_left_side, self.params.alpha_time)
        self.preys_trace = PreysTrace(self.movie_content, self.params)

        trace_point_wp = self.preys_trace.getTracePointPosition(0)

        self.prey.setPosition(trace_point_wp)

        if self.params.trace is None or len(self.params.trace) == 0:
            self.preys_trace.setCurrentTextPoint(0)
        else:
            self.preys_trace.setCurrentTextPoint(self.params.trace[0])
            self.preys_trace.static_trace_rout_index = (self.preys_trace.static_trace_rout_index + 1) % len(self.preys_trace.static_trace_rout)

    def _onActivate(self):
        super(Hunt2d, self)._onActivate()

    def _onDeactivate(self):
        self.__cleanUp()
        super(Hunt2d, self)._onDeactivate()

    def __cleanUp(self):
        if self.tc_hunter is not None:
            self.tc_hunter.cancel()
            self.tc_hunter = None

        if self.tc_prey is not None:
            self.tc_prey.cancel()
            self.tc_prey = None

        self.__removeMousePositionProvider()

        if self.hunters_hand is not None:
            self.hunters_hand.weapon.cleanUp()
        self.hunters_hand = None

        if self.prey is not None:
            self.prey.cleanUp()
        self.prey = None

        if self.preys_trace is not None:
            self.preys_trace.semaphore_trace_end.setValue(True)
        self.preys_trace = None

        self.params = None
        self.movie_content = None

        if self.tc_first_launch is not None:
            self.tc_first_launch.cancel()
            self.tc_first_launch = None

    def __removeMousePositionProvider(self):
        if self.mouse_position_provider is not None:
            Mengine.removeMousePositionProvider(self.mouse_position_provider)
        self.mouse_position_provider = None

    def _playEnigma(self):
        self.__runTaskChains(True)

    def __runTaskChains(self, b_first_launch):
        self.tc_hunter = TaskManager.createTaskChain(Repeat=True)
        with self.tc_hunter as tc_hunter:
            if b_first_launch:
                semaphore_tc_first_launch_finish = Semaphore("Hunt2d_tc_first_launch_finish", False)

                self.tc_first_launch = TaskManager.createTaskChain()
                with self.tc_first_launch as tc:
                    if self.params.b_hunter_hand_alpha_in_on_first_play:
                        tc.addTask("TaskNodeAlphaTo", Node=self.hunters_hand.movie_hunters_hand.getEntityNode(), From=0.0, To=1.0, Time=self.params.alpha_time)
                        tc.addFunction(self.hunters_hand.movie_hunters_hand.setAlpha, 1.0)  # save alpha=1.0 to group

                    tc.addSemaphore(semaphore_tc_first_launch_finish, To=True)

                tc_hunter.addSemaphore(semaphore_tc_first_launch_finish, From=True)

            tc_hunter.addTask('TaskMovie2SocketClick', Movie2=self.movie_content, SocketName='game_area')
            tc_hunter.addSemaphore(self.semaphore_resolve_shot, To=True)
            tc_hunter.addScope(self.__scopeResolveShot)
            tc_hunter.addSemaphore(self.semaphore_resolve_shot, To=False)

        self.tc_prey = TaskManager.createTaskChain(Repeat=True)
        with self.tc_prey as tc_prey:
            tc_prey.addFunction(self.preys_trace.createNewTrace)
            with tc_prey.addRepeatTask() as (tc_prey_repeat, tc_prey_until):
                tc_prey_repeat.addScope(self.__scopeMovePrey)
                tc_prey_repeat.addFunction(self.preys_trace.checkTraceEnd)

                tc_prey_until.addSemaphore(self.preys_trace.semaphore_trace_end, From=True, To=False)

            tc_prey.addDelay(self.preys_trace.getFinishDelay())

    def __scopeResolveShot(self, source):
        speed = DefaultManager.getDefaultFloat(self.params.bullet_move_speed_default_value, 0.2)

        weapon = self.hunters_hand.weapon
        shot_point = self.__getShotPoint()
        source.addDisable(weapon.movie_weapon_in_hand)

        source.addEnable(weapon.movie_weapon_shot_effect)
        source.addPlay(weapon.movie_weapon_shot_effect, Wait=True)
        source.addDisable(weapon.movie_weapon_shot_effect)

        source.addScope(self.hunters_hand.prepareToShot)
        source.addPlay(weapon.movie_weapon_in_attack, Loop=True, Wait=False)
        source.addTask("AliasObjectMoveTo", Object=weapon.movie_weapon_in_attack, To=shot_point, Speed=speed)

        source.addDisable(weapon.movie_weapon_in_attack)

        with source.addIfTask(self.prey.checkHit, shot_point) as (source_success, source_fail):
            source_success.addSemaphore(self.preys_trace.semaphore_trace_end, To=True)
            source_success.addFunction(self.tc_prey.setRepeat, False)
            source_success.addNotify(Notificator.onHunt2dPreyHit)
            source_success.addScope(self.__scopePlayWinsAnimations)
            source_success.addFunction(self.__completeEnigma)

            with GuardBlockInput(source_fail) as guard_source_fail:
                guard_source_fail.addEnable(weapon.movie_weapon_start)
                guard_source_fail.addPlay(weapon.movie_weapon_start, Wait=True, Loop=False)
                guard_source_fail.addDisable(weapon.movie_weapon_start)

        source.addEnable(weapon.movie_weapon_in_hand)
        source.addPlay(weapon.movie_weapon_in_hand, Loop=True, Wait=False)

    def __scopePlayWinsAnimations(self, source):
        with source.addParallelTask(2) as (source_prey, source_hand):
            source_prey.addScope(self.prey.scopePlayDeathAnimation)

            source_hand.addScope(self.hunters_hand.scopePlayHideAnimation)

    def __setPreyOnNewTracePoint(self):
        next_trace_point_index = self.preys_trace.getNextTracePointIndex()
        next_trace_point_wp = self.preys_trace.getTracePointPosition(next_trace_point_index)

        self.prey.setPosition(next_trace_point_wp)

        self.preys_trace.setCurrentTextPoint(next_trace_point_index)

    def __getMovingVector(self, first_point, second_point):
        if first_point.x <= second_point.x:
            return 'right'
        return 'left'

    def __scopeMovePrey(self, source):
        next_trace_point_index = self.preys_trace.getNextTracePointIndex()

        start_point_wp = self.prey.getPosition()
        finish_point_wp = self.preys_trace.getTracePointPosition(next_trace_point_index)

        bezier_coordinates = self.__getBezierCoordinates(start_point_wp, finish_point_wp)
        side = self.__getMovingVector(start_point_wp, finish_point_wp)

        with source.addParallelTask(2) as (source_disable_idle, source_enable_run):
            source_disable_idle.addScope(self.prey.scopeAlphaTo, "idle", False)
            source_disable_idle.addFunction(self.prey.disableIdleState)

            source_enable_run.addScope(self.prey.scopeTurnedTo, side)
            source_enable_run.addFunction(self.prey.enableRunMode, side)
            source_enable_run.addScope(self.prey.scopeAlphaTo, "run", True)

        source.addTask("AliasObjectBezier2To", Object=self.prey.movie_prey_body_box, Point1=bezier_coordinates, To=finish_point_wp, Speed=self.preys_trace.trace_speed)

        with source.addParallelTask(2) as (source_disable_run, source_enable_idle):
            source_disable_run.addScope(self.prey.scopeAlphaTo, "run", False)
            source_disable_run.addFunction(self.prey.disableRunMode)
            source_disable_run.addFunction(self.__setPreyOnNewTracePoint)

            source_enable_idle.addFunction(self.prey.setIdleState, side)
            source_enable_idle.addScope(self.prey.scopeAlphaTo, "idle", True)

    def __getBezierCoordinates(self, start_point, finish_point):
        if start_point.y >= finish_point.y:
            return start_point.x, finish_point.y
        return finish_point.x, start_point.y

    def __getShotPoint(self):
        sight_point = self.hunters_hand.getSightPosition()

        val = 0
        for (i, trace_point) in self.preys_trace.prey_trace_points.iteritems():
            if sight_point.x > self.preys_trace.getTracePointPosition(i).x and val < i:
                val = i

        if val == len(self.preys_trace.prey_trace_points) - 1:  # if sight_point is farther than the extreme right point
            val -= 1

        left_point = self.preys_trace.getTracePointPosition(val)
        right_point = self.preys_trace.getTracePointPosition(val + 1)

        return self.__getBezier2AndSightCrossPoint(left_point, right_point, sight_point)

    def __getBezier2AndSightCrossPoint(self, left_point, right_point, sight_point):
        ax, bx, cx, dx = left_point.x, left_point.x, right_point.x, sight_point.x
        ay, by, cy = left_point.y, left_point.y, right_point.y
        v = (-ax * cx + ax * dx + pow(bx, 2) + cx * dx - 2 * bx * dx)
        if v < 0:
            v = 1
        t = ((ax - bx) + pow(v, 0.5) / (ax - 2 * bx + cx))

        y = ay * pow((1 - t), 2) + 2 * t * by * (1 - t) + cy * pow(t, 2)

        return sight_point.x, y - 50  # need to fix "-50" it`s not ok

    def __completeEnigma(self):
        self.enigmaComplete()
        self.__cleanUp()

    def _restoreEnigma(self):
        self.__runTaskChains(False)

    def _resetEnigma(self):
        pass

    def _skipEnigma(self):
        self.__cleanUp()

    def _stopEnigma(self):
        pass