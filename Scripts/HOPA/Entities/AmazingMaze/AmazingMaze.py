from math import atan2

from Event import Event
from Foundation.TaskManager import TaskManager
from HOPA.AmazingMazeManager import AmazingMazeManager


Enigma = Mengine.importEntity("Enigma")


class DirectionMovie(object):
    """
    class which take 4 sub movies of main movie, to resolve and play right sub movie: right, left, up or down
    """

    def __init__(self, movie, sub_suffix):
        self.main = movie

        self.up, self.down, self.left, self.right = self.__setupSubMovies(movie, sub_suffix)

        self.current = self.down

        self.up.setEnable(False)
        self.left.setEnable(False)
        self.right.setEnable(False)

    @staticmethod
    def __setupSubMovies(movie, sub_suffix):
        suffixes = ['Up', 'Down', 'Left', 'Right']
        movies = [movie.entity.getSubMovie(sub_suffix + suffix) for suffix in suffixes]
        return movies

    def setEnable(self, value):
        self.main.setEnable(value)

    def setPlay(self, value):
        self.main.setPlay(value)

    def setLoop(self, value):
        self.main.setLoop(value)

    @staticmethod
    def __subMovieSetPlay(submovie, value):
        anim = submovie.getAnimation()
        anim.setLoop(value)
        anim.play() if value else anim.stop()

    def __changeSubMovie(self, sub_movie):
        if sub_movie is self.current:
            return

        self.current.setEnable(False)
        self.__subMovieSetPlay(self.current, False)

        sub_movie.setEnable(True)
        self.__subMovieSetPlay(sub_movie, True)
        self.current = sub_movie

    def changeDirection(self, pos_2):
        pos_1 = self.main.entity.node.getWorldPosition()
        delta_x = pos_2[0] - pos_1[0]
        delta_y = pos_2[1] - pos_1[1]

        if delta_x - delta_y > 0:
            if abs(delta_x) > abs(delta_y):
                self.__changeSubMovie(self.right)
            else:
                self.__changeSubMovie(self.up)
        else:
            if abs(delta_x) > abs(delta_y):
                self.__changeSubMovie(self.left)
            else:
                self.__changeSubMovie(self.down)


class HeroAnimHandler(object):
    """
    class which take hero movies and move type parameter (rotate or change direction) and resolve it's logic
    """

    def __init__(self, hero_movie, hero_move_movie, hero_idle_movie, hero_finish_movie, hero_move_mode, rotation_speed):
        self.hero_movie = hero_movie
        self.hero_move_mode = hero_move_mode

        self.stateMovies = dict()
        self.curStateMovie = None

        self.hero_movie_node = hero_movie.getEntityNode()
        self.hero_movie_node.addChild(hero_idle_movie.getEntityNode())
        self.hero_movie_node.addChild(hero_move_movie.getEntityNode())
        self.hero_movie_node.addChild(hero_finish_movie.getEntityNode())

        if self.hero_move_mode is 0:
            self.stateMovies['idle'] = DirectionMovie(hero_idle_movie, 'idle')
            self.stateMovies['move'] = DirectionMovie(hero_move_movie, 'move')
            self.stateMovies['finish'] = hero_finish_movie

        elif self.hero_move_mode is 1:
            self.stateMovies['idle'] = hero_idle_movie
            self.stateMovies['move'] = hero_move_movie
            self.stateMovies['finish'] = hero_finish_movie

        else:
            Trace.log("Entity", 0, "AmazingMaze HeroAnimHandler.__init__(), unknown hero_move_mode!! Please, set to 0 or 1")

        # handle defaults
        self.stateMovies['move'].setEnable(False)
        self.stateMovies['finish'].setEnable(False)
        self.curStateMovie = self.stateMovies['idle']
        self.curStateName = 'idle'
        self.__enableCurStateMovie(True)

        self.__timer = 0.0
        self.__lerpRotationAffectorRef = None

        self._b_finish_state_played = False

        self.rotation_speed = rotation_speed

    def changeDirectionTo(self, direction):
        if self.hero_move_mode is 0:
            self.curStateMovie.changeDirection(direction)  # swap submovie

        elif self.hero_move_mode is 1:  # rotate
            self.lerpRotation(direction)

        else:
            Trace.log("Entity", 0, "AmazingMaze HeroAnimHandler.changeDirectionTo(), unknown hero_move_mode!! Please, set to 0 or 1")

    def __lerpRotationAffector(self, delta_time, node, rotation_from, rotation_to, time):
        delta_rotation = (rotation_to - rotation_from) * delta_time / time

        current_rotation = node.getAngle() + delta_rotation

        self.__timer += delta_time
        if self.__timer >= time:
            self.__timer = 0.0
            node.setAngle(rotation_to % 6.28319)
            return True

        node.setAngle(current_rotation)
        return False

    def lerpRotation(self, direction):
        node = self.hero_movie_node
        node_pos = node.getLocalPosition()

        rotate_from = node.getAngle()

        vec_1 = Mengine.vec2f(0, -node_pos.y)
        vec_2 = Mengine.vec2f(direction.x - node_pos.x, direction.y - node_pos.y)

        dot = vec_2.x * vec_1.x + vec_2.y * vec_1.y
        det = vec_2.x * vec_1.y - vec_2.y * vec_1.x

        rotate_to = atan2(det, dot)

        positive_angle = rotate_to % 6.28319
        negative_angle = positive_angle - 6.28319

        positive_angle_delta = positive_angle - rotate_from
        negative_angle_delta = negative_angle - rotate_from

        if abs(positive_angle_delta) < abs(negative_angle_delta):
            smaller_angle = positive_angle
        else:
            smaller_angle = negative_angle

        if self.__lerpRotationAffectorRef is not None:
            Mengine.removeAffector(self.__lerpRotationAffectorRef)

        self.__lerpRotationAffectorRef = Mengine.addAffector(self.__lerpRotationAffector, node, rotate_from,
                                                             smaller_angle, self.rotation_speed)

    def getStateMovie(self, state_name):
        return self.stateMovies[state_name]

    def __setCurState(self, state_name):
        self.curStateName = state_name
        self.curStateMovie = self.stateMovies[state_name]

    def __enableCurStateMovie(self, enable, play=True, loop=True):
        self.curStateMovie.setEnable(enable)
        self.curStateMovie.setPlay(play)
        self.curStateMovie.setLoop(loop)

    def changeCurStateMovie(self, state_name, play=True, loop=True):
        if self._b_finish_state_played:
            return

        if self.curStateName == state_name:
            return

        self.__enableCurStateMovie(False, False, False)
        self.__setCurState(state_name)
        self.__enableCurStateMovie(True, play, loop)

    def playFinishAnim(self, source):
        self._b_finish_state_played = True

        for movie in self.stateMovies.values():
            movie.setEnable(False)

        self.curStateMovie = self.getStateMovie("finish")
        self.curStateMovie.setEnable(True)
        source.addPlay(self.curStateMovie)

    def cleanUp(self):
        if self.__lerpRotationAffectorRef is not None:
            Mengine.removeAffector(self.__lerpRotationAffectorRef)


class CursorMoviesHandler(object):
    POINTER_PLACED = 0
    POINTER_ACTIVE = 1
    POINTER_REACHED = 2

    def __init__(self, movie_pointer_placed, movie_pointer_reached, movie_pointer_active, maze_entity):
        self.movie_pointer_placed = movie_pointer_placed
        self.movie_pointer_reached = movie_pointer_reached
        self.movie_pointer_active = movie_pointer_active

        self.pointer_node = Mengine.createNode("Interender")
        self.pointer_node.enable()
        maze_entity.addChildFront(self.pointer_node)

        self.movies = {
            self.POINTER_PLACED: movie_pointer_placed,
            self.POINTER_ACTIVE: movie_pointer_active,
            self.POINTER_REACHED: movie_pointer_reached
        }

        for movie in self.movies.values():
            movie.setEnable(False)
            movie.setPlay(False)
            movie.setLoop(False)

            self.pointer_node.addChild(movie.entity.node)

        self.current_pointer_movie = movie_pointer_placed

    def __setDefaultMovieStates(self):
        for movie in self.movies.values():
            movie.setEnable(False)
            movie.setPlay(False)
            movie.setLoop(False)

    def __setPointerActive(self):
        self.__setDefaultMovieStates()

        self.current_pointer_movie = self.movies[self.POINTER_ACTIVE]

        self.current_pointer_movie.setEnable(True)
        self.current_pointer_movie.setLoop(True)
        self.current_pointer_movie.setPlay(True)

    def setPointerPlaced(self, pos):
        self.__setDefaultMovieStates()

        self.pointer_node.setLocalPosition(pos)

        self.current_pointer_movie = self.movies[self.POINTER_PLACED]

        self.current_pointer_movie.setLastFrame(False)
        self.current_pointer_movie.setEnable(True)

        with TaskManager.createTaskChain() as tc:
            tc.addPlay(self.current_pointer_movie)
            tc.addFunction(self.__setPointerActive)

    def setPointerReached(self, pos):
        self.__setDefaultMovieStates()

        self.pointer_node.setLocalPosition(pos)

        self.current_pointer_movie = self.movies[self.POINTER_REACHED]

        self.current_pointer_movie.setLastFrame(False)
        self.current_pointer_movie.setEnable(True)

        with TaskManager.createTaskChain() as tc:
            tc.addPlay(self.current_pointer_movie)
            tc.addDisable(self.current_pointer_movie)

    def cleanUp(self):
        for movie in self.movies.values():
            movie.returnToParent()

        self.pointer_node.removeFromParent()
        Mengine.destroyNode(self.pointer_node)
        self.pointer_node = None


class AmazingMaze(Enigma):
    def __init__(self):
        super(AmazingMaze, self).__init__()
        self.param = None

        self.movie_hero = None
        self.movie_finish = None
        self.movie_finish_reached = None
        self.movie_maze = None

        self._tc_main = None
        self._tc_complete = None
        self._tick_affector = None

        self._hero_anim_handler = None
        self._cursor_movies_handler = None

        self._hero_node = None
        self._hero_node_collider = None
        self._wall_colliders = []

        self._finish_hotspot = None

        # params
        self.init_speed = 40.0
        self.max_speed = 80.0
        self.acceleration = 500.0
        self.breaking_mult = 4.0
        self.target_reach_distance_threshold = 15.0
        self.zero_velocity_threshold = 5.0
        #

        self._b_should_launch = True  # set init velocity
        self._velocity = Mengine.vec2f(0.0, 0.0)
        self._current_speed = 0.0

        self._target_pos = None

        self.completeEvent = Event("AmazingMazeComplete")

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParam(self):
        self.param = AmazingMazeManager.getParam(self.EnigmaName)

    def _setup(self):
        self.movie_hero = self.object.getObject(self.param.HeroNode)
        self._hero_node = self.movie_hero.getEntityNode()
        self._hero_node.setLocalPosition(self.param.HeroSpawnPoint)

        polygon = self.movie_hero.getSocket('socket').getPolygon()
        anchor = self.movie_hero.getSocket('socket').getLocalOrigin()
        self._hero_node_collider = Mengine.createNode("HotSpotPolygon")
        self._hero_node_collider.setName('HeroNodeCollider')
        self._hero_node_collider.setPolygon(polygon)
        self._hero_node_collider.setLocalOrigin(anchor)
        self._hero_node_collider.enable()
        self.node.addChild(self._hero_node_collider)
        self._hero_node_collider.setLocalPosition(self.param.HeroSpawnPoint)

        self.movie_maze = self.object.getObject(self.param.Maze)
        self._wall_colliders = [socket for (movie, socket_name, socket) in
            self.movie_maze.getEntity().movie.getSockets()]

        movie_hero_move = self.object.getObject(self.param.HeroMove)
        movie_hero_idle = self.object.getObject(self.param.HeroIdle)
        movie_hero_finish = self.object.getObject(self.param.HeroFinish)
        self._hero_anim_handler = HeroAnimHandler(self.movie_hero, movie_hero_move, movie_hero_idle, movie_hero_finish,
                                                  self.param.MoveMode, self.param.RotationSpeed)

        self.movie_finish = self.object.getObject(self.param.FinishIdle)
        self.movie_finish.setPlay(True)
        self.movie_finish.setLoop(True)
        self.movie_finish_reached = self.object.getObject(self.param.FinishReached)
        self.movie_finish_reached.setEnable(False)

        self._finish_hotspot = self.movie_finish.getSocket("socket")

        self.init_speed = self.param.InitSpeed
        self.max_speed = self.param.MaxSpeed
        self.acceleration = self.param.Acceleration
        self.breaking_mult = self.param.BreakingMult
        self.target_reach_distance_threshold = self.param.TargetReachDistanceThreshold
        self.zero_velocity_threshold = self.param.ZeroVelocityThreshold

        if self.param.bUseCursorPointer:
            self._cursor_movies_handler = CursorMoviesHandler(self.object.getObject(self.param.PointerPlaced),
                                                              self.object.getObject(self.param.PointerReached),
                                                              self.object.getObject(self.param.PointerActive),
                                                              self.movie_maze.getEntityNode())

    def __activate(self):
        self._tick_affector = Mengine.addAffector(self.__tickAffector)

    def _removeTickAffector(self):
        if self._tick_affector is not None:
            Mengine.removeAffector(self._tick_affector)
            self._tick_affector = None

    def _cleanUp(self):
        self._removeTickAffector()
        self._target_pos = None

        if self._cursor_movies_handler is not None:
            self._cursor_movies_handler.cleanUp()
            self._cursor_movies_handler = None

        if self._hero_anim_handler is not None:
            self._hero_anim_handler.cleanUp()
            self._hero_anim_handler = None

        if self._tc_main is not None:
            self._tc_main.cancel()
            self._tc_main = None

        if self._hero_node_collider is not None:
            Mengine.destroyNode(self._hero_node_collider)
            self._hero_node_collider = None

        if self._tc_complete is not None:
            self._tc_complete.cancel()
            self._tc_complete = None

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def __computeMovePosition(self, from_pos, to_pos, delta_time):
        """compute velocity:
        v = v0 + a*t

        compute movement delta:
        Velocity Verlet integration (http://en.wikipedia.org/wiki/Verlet_integration#Velocity_Verlet)
        p = p0 + v0*t + 1/2*a*t^2
        p = p0 + v0*t + 1/2*((v1-v0)/t)*t^2
        p = p0 + v0*t + 1/2*((v1-v0))*t
        """

        delta_sec = delta_time / 1000.0

        direction = to_pos - from_pos
        direction_magnitude = Mengine.length_v2(direction)

        if direction_magnitude >= self.target_reach_distance_threshold:
            direction.x, direction.y = direction.x / direction_magnitude, direction.y / direction_magnitude  # normalize
            accelerated_velocity = direction * (self.acceleration * delta_sec * 0.5)  # accelerate in direction

        else:
            # braking: add counter force
            accelerated_velocity = self._velocity * (- delta_sec * 0.5 * self.breaking_mult)
            self.__onTargetReached()  # target reach handle

        if self._b_should_launch:  # first launch
            self._b_should_launch = False
            self._velocity = direction * self.init_speed
        else:
            self._velocity = self._velocity + accelerated_velocity

        velocity_size = Mengine.length_v2(self._velocity)  # speed limiter
        if velocity_size > self.max_speed:
            self._velocity.x = self.max_speed * self._velocity.x / velocity_size
            self._velocity.y = self.max_speed * self._velocity.y / velocity_size
        elif velocity_size <= self.zero_velocity_threshold:
            self._velocity.x, self._velocity.y = 0.0, 0.0

        self._current_speed = velocity_size

        new_pos = from_pos + self._velocity * delta_sec

        return new_pos

    def __isCollidingWithWalls(self, node):
        for wall in self._wall_colliders:
            if Mengine.testHotspot(wall, node) and wall.getName() != "click_area":
                return True
        return False

    def __changePositionWithSweep(self, old_pos, new_pos):
        """
        :param old_pos: prev pos
        :param new_pos: new pos
        :return: true if collided, false if not
        """
        if self._hero_node_collider is None:
            return False

        self._hero_node_collider.setWorldPosition(new_pos)

        if self.__isCollidingWithWalls(self._hero_node_collider):
            self._hero_node_collider.setWorldPosition(old_pos)
            return True
        elif self.__checkFinish() is True:
            self._hero_node.setWorldPosition(new_pos)
            return False
        else:
            self._hero_node.setWorldPosition(new_pos)
            return False

    def __handleMovementAnimation(self):
        if self._hero_anim_handler is None:
            return

        if self._current_speed <= self.zero_velocity_threshold:
            self._hero_anim_handler.changeCurStateMovie('idle')
        else:
            self._hero_anim_handler.changeCurStateMovie('move')

    def __updateTargetPosition(self):
        self._target_pos = Mengine.getCursorPosition()
        self._hero_anim_handler.changeDirectionTo(self._target_pos)
        self._b_should_launch = True

        if self._cursor_movies_handler is not None:
            self._cursor_movies_handler.setPointerPlaced(self._target_pos)

    def __updateTargetPositionDown(self):
        """ updater for mobile devices when mouse is down """
        self._target_pos = Mengine.getCursorPosition()
        self._hero_anim_handler.changeDirectionTo(self._target_pos)

        if self._cursor_movies_handler is not None:
            self._cursor_movies_handler.pointer_node.setLocalPosition(self._target_pos)

    def __onTargetReached(self):
        if self._cursor_movies_handler is not None and self._target_pos is not None:
            self._cursor_movies_handler.setPointerReached(self._target_pos)

        self._target_pos = None

    def __checkFinish(self):
        if self._hero_node_collider is None or self._finish_hotspot is None:
            return False

        if Mengine.testHotspot(self._hero_node_collider, self._finish_hotspot):
            self.completeEvent()
            return True
        return False

    def __tickAffector(self, delta_time):
        hero_pos = self._hero_node.getWorldPosition()
        target_pos = self._target_pos if self._target_pos is not None else hero_pos

        new_hero_pos = self.__computeMovePosition(hero_pos, target_pos, delta_time)

        if self.__changePositionWithSweep(hero_pos, new_hero_pos):
            self._velocity = Mengine.vec2f(0.0, 0.0)
            self.__onTargetReached()

        self.__handleMovementAnimation()

        return False

    def __scopePlayFinishFX(self, source):
        with source.addParallelTask(2) as (parallel_0, parallel_1):
            if self.movie_finish_reached is not None:
                self.movie_finish.setEnable(False)

                self.movie_finish_reached.setPlay(False)
                self.movie_finish_reached.setLastFrame(False)
                self.movie_finish_reached.setEnable(True)

                parallel_0.addPlay(self.movie_finish_reached)

            else:
                parallel_0.addDummy()

            if self._hero_anim_handler is not None:
                self._hero_anim_handler.changeCurStateMovie('finish', False, False)

                parallel_1.addScope(self._hero_anim_handler.playFinishAnim)

            else:
                parallel_1.addDummy()

    def _scopeUpdateTargetPositionPC(self, source):
        source.addTask("TaskMovie2SocketClick", SocketName="click_area", Movie2Name="Movie2_maze", Group=self.object)
        source.addFunction(self.__updateTargetPosition)

    def _scopeUpdateTargetPositionMobile(self, source):
        source.addTask("TaskMovie2SocketClick", isDown=True, SocketName="click_area",
                       Movie2Name="Movie2_maze", Group=self.object)
        source.addFunction(self.__updateTargetPosition)

        with source.addRepeatTask() as (repeat, until):
            repeat.addTask("TaskMouseMove", Tracker=lambda *_: True)
            repeat.addFunction(self.__updateTargetPositionDown)

            until.addTask("TaskMouseButtonClick", isDown=False)

    def _runTaskChains(self):
        if self._tc_main is not None:
            self._tc_main.cancel()

        self._tc_main = TaskManager.createTaskChain(Repeat=True)
        with self._tc_main as tc:
            if Mengine.hasTouchpad() is True:
                tc.addScope(self._scopeUpdateTargetPositionMobile)
            else:
                tc.addScope(self._scopeUpdateTargetPositionPC)

        if self._tc_complete is not None:
            self._tc_complete.cancel()

        self._tc_complete = TaskManager.createTaskChain()
        with self._tc_complete as tc:
            tc.addEvent(self.completeEvent)
            tc.addFunction(self._tc_main.cancel)
            tc.addFunction(self._removeTickAffector)
            tc.addScope(self.__scopePlayFinishFX)
            tc.addFunction(self.enigmaComplete)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(AmazingMaze, self)._onPreparation()

        self._loadParam()

    def _onActivate(self):
        super(AmazingMaze, self)._onActivate()

        self._setup()
        self.__activate()

    def _onDeactivate(self):
        self._cleanUp()

        super(AmazingMaze, self)._onDeactivate()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._runTaskChains()

    def _restoreEnigma(self):
        self._runTaskChains()

    def _resetEnigma(self):
        self._cleanUp()
        self._setup()
        self.__activate()
        self._runTaskChains()

    def _stopEnigma(self):
        self._cleanUp()

    def _skipEnigma(self):
        self._tc_main.cancel()
