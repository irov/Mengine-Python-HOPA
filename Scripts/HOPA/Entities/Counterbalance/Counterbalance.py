from math import atan2

from Foundation.GroupManager import GroupManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.CounterbalanceManager import CounterbalanceManager


Enigma = Mengine.importEntity("Enigma")


# todo: parameterize rope hand scaling
# todo: rope hand attach to new special created top layer
# todo: maybe add appearing from alpha
# todo: bug sometimes movie2_rope_hand don't appear (in node debugger too, same bug as in MoveChipsOnGraphNodes)
# todo: fancy skip


def CREATE_BOX_POLYGON(size):
    size = size / 2.0
    top_left = (-size, -size)
    top_right = (size, -size)
    bottom_right = (size, size)
    bottom_left = (-size, size)
    return [top_left, top_right, bottom_right, bottom_left]


def CREATE_HOT_SPOT_GRID_WITH_CHILD_MOVIES(parent_node, child_nodes, child_name_suffix,
                                           matrix_size, distance, first_pos, hotspot_size):
    nodes = list()

    for j in range(matrix_size[1]):
        for i in range(matrix_size[0]):
            pos = (i * distance[0] + first_pos[0], j * distance[1] + first_pos[1])
            index = j * matrix_size[0] + i

            child = child_nodes[index]
            if child is not None:
                node = Mengine.createNode("HotSpotPolygon")
                node.setName(str(child_name_suffix) + str(index))

                node.setPolygon(CREATE_BOX_POLYGON(hotspot_size))
                node.setLocalPosition(pos)

                parent_node.addChild(node)
                node.addChild(child.getEntityNode())
                nodes.append(node)

    return nodes


def GET_VEC_ATAN_2(vec_1, vec_2):
    dot = vec_1.x * vec_2.x + vec_1.y * vec_2.y
    det = vec_1.x * vec_2.y - vec_1.y * vec_2.x
    return atan2(det, dot)


def DOT_DIST(dot_1, dot_2):
    return Mengine.length_v2_v2(dot_1, dot_2)


def NORMALIZE_DIST(dist, normal):
    return dist / normal


def NUM_IN_BOUNDARIES(num, min_, max_):
    return max(min(max_, num), min_)


def EDIT_DISABLE_LAYERS(id_, state, From):
    disabled = From.getParam('DisableLayers')
    if state is True and id_ in disabled:
        From.delParam('DisableLayers', id_)
    elif state is False and id_ not in disabled:
        From.appendParam('DisableLayers', id_)


class Rope(object):
    def __init__(self, movie, wheel):
        self.__movie = movie
        self.__wheel = wheel

        self.__enabled_sprites = list()

        self.__attachToWheelParentNode()
        self.__disableAllSprites()
        self.enableCorrectSprite()
        self.__movie.setEnable(True)

    def __attachToWheelParentNode(self):
        parent_node = self.__wheel.getParentNode()
        node = self.__movie.getEntityNode()
        parent_node.addChild(node)

    def __disableAllSprites(self):
        self.__movie.appendParam("DisableLayers", 'Sprite_Left')
        self.__movie.appendParam("DisableLayers", 'Sprite_Right')
        self.__movie.appendParam("DisableLayers", 'Sprite_Down')
        self.__movie.appendParam("DisableLayers", 'Sprite_Up')
        self.__movie.appendParam("DisableLayers", 'Sprite_Horizontal')
        self.__movie.appendParam("DisableLayers", 'Sprite_Vertical')

    def __setSprites(self, *sprites):
        for sprite in self.__enabled_sprites:
            # self.__movie.appendParam("DisableLayers", sprite)
            EDIT_DISABLE_LAYERS(sprite, False, self.__movie)
        for sprite in sprites:
            # self.__movie.delParam("DisableLayers", sprite)
            EDIT_DISABLE_LAYERS(sprite, True, self.__movie)
        self.__enabled_sprites = sprites

    @staticmethod
    def __getRelativeWheelPos(from_wheel, to_wheel):
        for direction, wheel in to_wheel.getNeighbors().items():
            if wheel == from_wheel:
                return direction

    def getMovie(self):
        return self.__movie

    def enableCorrectSprite(self):
        prev = self.__wheel.getPrev()
        cur = self.__wheel
        next_ = self.__wheel.getNext()

        if prev is None:
            pos = Rope.__getRelativeWheelPos(next_, cur)

            if pos is 'up':
                self.__setSprites('Sprite_Up')
            elif pos is 'right':
                self.__setSprites('Sprite_Right')
            elif pos is 'down':
                self.__setSprites('Sprite_Down')
            else:
                self.__setSprites('Sprite_Left')

        elif next_ is None:
            pos = Rope.__getRelativeWheelPos(prev, cur)

            if pos is 'up':
                self.__setSprites('Sprite_Up')
            elif pos is 'right':
                self.__setSprites('Sprite_Right')
            elif pos is 'down':
                self.__setSprites('Sprite_Down')
            else:
                self.__setSprites('Sprite_Left')

        else:
            pos_prev = Rope.__getRelativeWheelPos(prev, cur)
            pos_next = Rope.__getRelativeWheelPos(next_, cur)

            if pos_prev is 'up':
                if pos_next is 'right':
                    self.__setSprites('Sprite_Up', 'Sprite_Right')
                elif pos_next is 'left':
                    self.__setSprites('Sprite_Up', 'Sprite_Left')
                else:
                    self.__setSprites('Sprite_Vertical')

            elif pos_prev is 'down':
                if pos_next is 'right':
                    self.__setSprites('Sprite_Down', 'Sprite_Right')
                elif pos_next is 'left':
                    self.__setSprites('Sprite_Down', 'Sprite_Left')
                else:
                    self.__setSprites('Sprite_Vertical')

            elif pos_prev is 'left':
                if pos_next is 'up':
                    self.__setSprites('Sprite_Left', 'Sprite_Up')
                elif pos_next is 'down':
                    self.__setSprites('Sprite_Left', 'Sprite_Down')
                else:
                    self.__setSprites('Sprite_Horizontal')

            else:
                if pos_next is 'up':
                    self.__setSprites('Sprite_Right', 'Sprite_Up')
                elif pos_next is 'down':
                    self.__setSprites('Sprite_Right', 'Sprite_Down')
                else:
                    self.__setSprites('Sprite_Horizontal')

    def scopePlay(self, source):
        source.addPlay(self.__movie, Wait=False, Loop=True)

    def cleanUp(self):
        if self.__movie is not None:
            node = self.__movie.getEntityNode()
            if node is not None:
                if node.hasParent():
                    node.removeFromParent()

            self.__movie.onFinalize()
            self.__movie.onDestroy()


class RopeManager(object):
    def __init__(self, rope_hand_movie, rope_movies_generator, teams_params):
        self.__hand_movie = rope_hand_movie
        self.__movie_generator = rope_movies_generator

        self.__rope_prototype_names = dict()
        self.__rope_hand_movie_sprite_names = dict()

        self.__current_hand_movie_sprite = None
        self.__ropes = list()

        self.__affector = None

        '''
        setup team rope prototypes names, disable team sprites for rope hand
        '''
        for team_name, team_param in teams_params.items():
            sprite_name = team_param['RopeHandSprite']
            # self.__hand_movie.appendParam("DisableLayers", sprite_name)
            EDIT_DISABLE_LAYERS(sprite_name, False, self.__hand_movie)

            self.__rope_hand_movie_sprite_names[team_name] = sprite_name
            self.__rope_prototype_names[team_name] = team_param['RopePrototype']

        '''
        set default rope spite, disable rope_hand
        '''
        self.__current_hand_movie_sprite = sprite_name
        self.__hand_movie.setEnable(False)

    @staticmethod
    def __rotateAndScaleRopeHand(_, self):
        node = self.__hand_movie.getEntityNode()
        node_pos = node.getWorldPosition()
        mouse_pos = Mengine.getCursorPosition()

        vec1 = Mengine.vec2f(0, -node_pos.y)
        vec2 = Mengine.vec2f(mouse_pos.x - node_pos.x, mouse_pos.y - node_pos.y)

        node.setAngle(GET_VEC_ATAN_2(vec2, vec1))

        dot_dist = DOT_DIST(mouse_pos, node_pos)
        normalized_dist = NORMALIZE_DIST(dot_dist, 100.0)
        dist_in_boundaries = NUM_IN_BOUNDARIES(normalized_dist, 0.7, 0.9)
        node.setScale((1.0, dist_in_boundaries, 1.0))
        return False

    def __changeRopeHandSprite(self, team):
        """
        disable current sprite for rope_hand sprite,
        set and enable new sprite for rope_hand
        """
        sprite_name = self.__rope_hand_movie_sprite_names[team]

        EDIT_DISABLE_LAYERS(self.__current_hand_movie_sprite, False, self.__hand_movie)
        EDIT_DISABLE_LAYERS(sprite_name, True, self.__hand_movie)
        self.__current_hand_movie_sprite = sprite_name

    def attachRopeHand(self, cb_get_wheel):
        """
        attaching rope hand on parent node of wheel movie-prototype,
        enable hand_movie

        enable affector for rotation and scaling rope_hand on node relative to cursor position
        """
        wheel = cb_get_wheel()
        self.__changeRopeHandSprite(wheel.getTeam())

        node = wheel.getParentNode()
        node.addChild(self.__hand_movie.getEntityNode())
        self.__hand_movie.setEnable(True)

        self.__affector = Mengine.addAffector(self.__rotateAndScaleRopeHand, self)

    def detachRopeHand(self):
        """
        detaching rope hand from current wheel's parent node

        disable affector
        """
        self.__hand_movie.setEnable(False)
        node = self.__hand_movie.getEntityNode()
        if node.hasParent():
            node.removeFromParent()

        Mengine.removeAffector(self.__affector)

    def createAndAttachRope(self, cb_get_wheel):
        """
        creating and attaching rope movie-prototype on wheel relatively to wheel team
        """
        wheel = cb_get_wheel()

        team = wheel.getTeam()
        rope_prototype = self.__rope_prototype_names[team]
        movie = self.__movie_generator(rope_prototype, rope_prototype, Enable=False)

        rope = Rope(movie, wheel)
        wheel.setRope(rope)

        self.__ropes.append(rope)

    def updateAttachedRope(self, cb_get_wheel):
        """
        calling enableCorrectSprite for rope of received wheel,
        if it's first wheel in chain, then create it first
        """
        wheel = cb_get_wheel()

        if wheel is not None:
            if wheel.getRope() is None:
                self.createAndAttachRope(cb_get_wheel)
                return

            rope = wheel.getRope()
            rope.enableCorrectSprite()

    def deleteRope(self, rope):
        if rope in self.__ropes:
            self.__ropes.remove(rope)

    def cleanUp(self):
        for rope in self.__ropes:
            rope.cleanUp()


class Wheel(object):
    def __init__(self, movie):
        self.__parent_node = movie.getEntityNode().getParent()
        self.__movie = movie
        self.__effect_movie = None

        self.__team = None
        self.__sibling = None

        self.__neighbors = dict()
        self.__next = None
        self.__prev = None

        self.__rope = None

    def getParentNode(self):
        return self.__parent_node

    def getMovie(self):
        return self.__movie

    def getTeam(self):
        return self.__team

    def setTeam(self, team_name):
        self.__team = team_name

    def isRoyal(self):
        return self.__sibling is not None

    def setSibling(self, wheel_obj):
        self.__sibling = wheel_obj

    def getSibling(self):
        return self.__sibling

    def setNeighbors(self, wheel_obj_dict):
        self.__neighbors = wheel_obj_dict

    def getNeighbors(self):
        return self.__neighbors

    def getNext(self):
        return self.__next

    def getPrev(self):
        return self.__prev

    def setPrev(self, wheel_obj):
        self.__prev = wheel_obj

    def setNext(self, wheel_obj):
        self.__next = wheel_obj
        wheel_obj.setPrev(self)

    def cleanUpNextPrev(self):
        self.__next = None
        self.__prev = None

    def setRope(self, rope_obj):
        self.__rope = rope_obj

    def getRope(self):
        return self.__rope

    def setEffectMovie(self, effect_movie):
        self.__effect_movie = effect_movie
        node = self.__movie.getEntityNode()
        node.addChild(effect_movie.getEntityNode())

    def scopeSocketClick(self, source):
        source.addTask("TaskNodeSocketClick", Socket=self.__parent_node, isDown=True)

    def scopeSocketEnter(self, source):
        source.addTask("TaskNodeSocketEnter", Socket=self.__parent_node)

    def scopePlay(self, source):
        if self.__effect_movie is not None:
            source.addEnable(self.__effect_movie)
            source.addPlay(self.__effect_movie, Wait=False)
        source.addPlay(self.__movie, Wait=False, Loop=True)
        source.addScope(self.__rope.scopePlay)

    def cleanUp(self):
        node = self.__movie.getEntityNode()
        if node.hasParent():
            node.removeFromParent()
        self.__movie.onFinalize()
        self.__movie.onDestroy()

        if self.__effect_movie is not None:
            node = self.__effect_movie.getEntityNode()
            if node.hasParent():
                node.removeFromParent()
            self.__effect_movie.onFinalize()
            self.__effect_movie.onDestroy()

        if self.__parent_node.hasParent():
            self.__parent_node.removeFromParent()
            Mengine.destroyNode(self.__parent_node)
            self.__parent_node = None


class WheelManager(object):
    def __init__(self, matrix_size, wheels_movies, object_generator, teams_params, continue_chain_mod):
        self.__wheels_by_name = dict()
        self.__wheels_by_index = dict()

        self.__wheels_team_sprites = dict()
        self.__team_complete_status = dict()

        self.__wheels_chain_initiators = list()

        self.__current_wheel = None
        self.__current_wheel_valid_neighbors = list()

        self.continue_chain_mod = continue_chain_mod
        '''
        wheel instances generator
        '''
        for movie in wheels_movies:
            if movie is None:
                continue

            index = wheels_movies.index(movie)
            wheel_name = movie.getName()

            wheel = Wheel(movie)

            self.__wheels_by_name[wheel_name] = wheel
            self.__wheels_by_index[index] = wheel

        '''
        setting up siblings, teams, movie_effect for royal wheels,
        setting up team parameters mappings for manager
        '''
        for team_name, team_param in teams_params.items():
            movie_effect = team_param['TeamEffectPrototype']
            wheel_king = self.__wheels_by_name[team_param['KingPrototype']]
            wheel_queen = self.__wheels_by_name[team_param['QueenPrototype']]

            wheel_king.setSibling(wheel_queen)
            wheel_queen.setSibling(wheel_king)

            wheel_king.setTeam(team_name)
            wheel_queen.setTeam(team_name)

            wheel_king.setEffectMovie(object_generator(movie_effect, movie_effect, Enable=False))
            wheel_queen.setEffectMovie(object_generator(movie_effect, movie_effect, Enable=False))

            self.__wheels_chain_initiators.append(wheel_king)
            self.__wheels_chain_initiators.append(wheel_queen)

            self.__team_complete_status[team_name] = False
            self.__wheels_team_sprites[team_name] = team_param['WheelPrototypeSprite']

        '''
        disable team sprites for common wheels
        '''
        for wheel in self.__wheels_by_name.values():
            if wheel.isRoyal():
                continue

            movie = wheel.getMovie()

            for team_sprite_name in self.__wheels_team_sprites.values():
                # movie.appendParam("DisableLayers", team_sprite_name)
                EDIT_DISABLE_LAYERS(team_sprite_name, False, movie)

        '''
        setting up wheel neighbors
        '''
        matrix_length = matrix_size[0]
        matrix_high = matrix_size[1]
        matrix_weight = matrix_high * matrix_length

        for wheel_index, wheel in self.__wheels_by_index.items():
            neighbors = dict()

            left_index = wheel_index - 1 if wheel_index % matrix_length != 0 else None
            up_index = wheel_index - matrix_length if wheel_index - matrix_length >= 0 else None
            right_index = wheel_index + 1 if wheel_index % matrix_length != matrix_length - 1 else None
            down_index = wheel_index + matrix_length if wheel_index + matrix_length < matrix_weight else None

            neighbors['left'] = self.__wheels_by_index.get(left_index)
            neighbors['up'] = self.__wheels_by_index.get(up_index)
            neighbors['right'] = self.__wheels_by_index.get(right_index)
            neighbors['down'] = self.__wheels_by_index.get(down_index)

            wheel.setNeighbors(neighbors)

    def getWheelTeamSpriteByTeam(self, team):
        return self.__wheels_team_sprites[team]

    def getWheelByName(self, name):
        return self.__wheels_by_name[name]

    def __setCurrentWheel(self, wheel):
        self.__current_wheel = wheel

    def getCurrentWheel(self):
        if self.__current_wheel is None:
            self.__current_wheel = self.__wheels_chain_initiators[0]

        return self.__current_wheel

    def getPreviousWheel(self):
        return self.__current_wheel.getPrev()

    def __currentWheelSetTeam(self):
        wheel = self.__current_wheel
        team = wheel.getPrev().getTeam()

        if wheel.getTeam() == team:
            return

        wheel.setTeam(team)

        sprite = self.__wheels_team_sprites[team]
        movie = wheel.getMovie()
        EDIT_DISABLE_LAYERS(sprite, True, movie)  # movie.delParam("DisableLayers", sprite)

    def __currentWheelSetValidNeighbors(self):
        """resolve next allowed wheel to be added in chain

        if neighbor wheel has no team then that is a regular wheel and can be next in chain

        if neighbor wheel team same as current wheel and neighbor wheel hasn't chained yet,
         then this is royal sibling of chain initiator, so it's should be last in chain
        """
        wheel = self.__current_wheel
        neighbors = []

        for neighbor in wheel.getNeighbors().values():
            if neighbor is None:
                continue
            if neighbor.getTeam() is None:
                neighbors.append(neighbor)
            else:
                if neighbor.getTeam() == wheel.getTeam() and neighbor.getNext() is None:
                    neighbors.append(neighbor)

        self.__current_wheel_valid_neighbors = neighbors

    def cleanWheelValidNeighbours(self):
        self.__current_wheel_valid_neighbors = list()

    def chainCanContinue(self):
        return bool(self.__current_wheel_valid_neighbors)

    def scopeStartChain(self, source):
        for wheel, race in source.addRaceTaskList(self.__wheels_chain_initiators):
            race.addScope(wheel.scopeSocketClick)
            race.addFunction(self.__setCurrentWheel, wheel)

        source.addFunction(self.__currentWheelSetValidNeighbors)

    def scopeContinueChain(self, source):
        semaphore = Semaphore(True, 'CounterbalanceChainRace')

        for wheel, race in source.addRaceTaskList(self.__current_wheel_valid_neighbors):
            race.addScope(wheel.scopeSocketEnter)
            race.addSemaphore(semaphore, From=True, To=False)
            race.addFunction(self.__current_wheel.setNext, wheel)
            race.addFunction(self.__setCurrentWheel, wheel)

        source.addFunction(self.__currentWheelSetTeam)
        source.addFunction(self.__currentWheelSetValidNeighbors)

    def scopePlayCurrentBuildedChain(self, source):
        wheel = self.__current_wheel
        source.addScope(wheel.scopePlay)

        while wheel.getPrev() is not None:
            wheel = wheel.getPrev()
            source.addScope(wheel.scopePlay)

    def isChainComplete(self):
        """
        remove previous chain initiator,
        if previous chain initiator is royal wheel, remove it's sibling, so
        we could't duplicate team chains

        set current wheel as chain initiator if chain is not complete

        return true if current chain complete, false is chain is not complete yet
        """
        if self.continue_chain_mod is True:
            prev_wheel = self.__current_wheel.getPrev()
            self.__wheels_chain_initiators.remove(prev_wheel)
            if prev_wheel.isRoyal():
                self.__wheels_chain_initiators.remove(prev_wheel.getSibling())

        if self.__current_wheel.isRoyal():
            if self.__current_wheel.getSibling().getNext() is not None:
                team = self.__current_wheel.getTeam()
                self.__team_complete_status[team] = True

                if self.continue_chain_mod is False:
                    self.__wheels_chain_initiators.remove(self.__current_wheel)
                    self.__wheels_chain_initiators.remove(self.__current_wheel.getSibling())
                return True

        if self.continue_chain_mod is True:
            self.__wheels_chain_initiators.append(self.__current_wheel)

        return False

    def isAllChainsComplete(self):
        return all(self.__team_complete_status.values())

    def cleanUp(self):
        for wheel in self.__wheels_by_index.values():
            wheel.cleanUp()


class Counterbalance(Enigma):
    def __init__(self):
        super(Counterbalance, self).__init__()
        self.tc = None
        self.params = None

        self.wheel_manager = None
        self.rope_manager = None

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParam(self):
        self.params = CounterbalanceManager.getParam(self.EnigmaName)

    def _setup(self):
        """
        setup
        """
        object_generator = self.object.generateObjectUnique

        rope_hand = self.object.getObject(self.params.rope_hand)

        wheels = self.params.wheels
        not_unique_wheels = set([wheel for wheel in wheels if wheel is not None and wheels.count(wheel) > 1])
        reward = GroupManager.getObject(self.object.getGroupName(), self.params.reward_movie)
        reward.setEnable(True)
        self.reward_node = reward.getEntityNode()

        '''
        generate wheel movies
        '''
        wheel_movies = []
        for i in range(len(wheels)):
            prototype = wheels[i]

            if prototype is None:
                wheel_movies.append(None)
                continue

            if prototype in not_unique_wheels:
                prototype_name = '{}_{}'.format(prototype, i)
            else:
                prototype_name = prototype

            wheel_movies.append(object_generator(prototype_name, prototype, Enable=True))

        '''
        creating HotSpotPolygon nodes grid and attaching wheel movies on it
        '''
        CREATE_HOT_SPOT_GRID_WITH_CHILD_MOVIES(self.node, wheel_movies, 'Wheel', self.params.matrix_size,
                                               self.params.distance, self.params.first_pos, self.params.hotspot_size)

        '''
        creating wheel and rope managers for separating and resolving game logic
        '''
        self.wheel_manager = WheelManager(self.params.matrix_size, wheel_movies, object_generator, self.params.teams,
                                          self.params.continue_chain_mod)
        self.rope_manager = RopeManager(rope_hand, object_generator, self.params.teams)

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.rope_manager is not None:
            self.rope_manager.cleanUp()

        if self.wheel_manager is not None:
            self.wheel_manager.cleanUp()

    def _nodeAlphaTo(self, Node, From, To, Time):
        with TaskManager.createTaskChain() as tc:
            tc.addTask('TaskNodeAlphaTo', Node=Node, From=From, To=To, Time=Time)

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def _runTaskChains(self):
        semaphore = Semaphore(False, 'CounterbalanceChainComplete')

        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            tc.addScope(self.wheel_manager.scopeStartChain)
            tc.addFunction(self.rope_manager.attachRopeHand, self.wheel_manager.getCurrentWheel)
            with tc.addRepeatTask() as (repeat, until):
                with repeat.addIfTask(self.wheel_manager.chainCanContinue) as (true, false):
                    true.addScope(self.wheel_manager.scopeContinueChain)
                    true.addFunction(self.rope_manager.detachRopeHand)
                    true.addFunction(self.rope_manager.attachRopeHand, self.wheel_manager.getCurrentWheel)
                    true.addFunction(self.rope_manager.updateAttachedRope, self.wheel_manager.getPreviousWheel)
                    true.addFunction(self.rope_manager.createAndAttachRope, self.wheel_manager.getCurrentWheel)

                    with true.addIfTask(self.wheel_manager.isChainComplete) as (true_source, _):
                        true_source.addScope(self.wheel_manager.scopePlayCurrentBuildedChain)
                        true_source.addSemaphore(semaphore, To=True)

                    false.addFunction(self.cleanUpCurrentWheelAndRopeLine, self.wheel_manager.getCurrentWheel)
                    false.addSemaphore(semaphore, To=True)

                with until.addRaceTask(2) as (race_1, race_2):
                    race_1.addTask("TaskMouseButtonClick", isDown=False)
                    if self.params.continue_chain_mod is False:
                        race_1.addFunction(self.cleanUpCurrentWheelAndRopeLine, self.wheel_manager.getCurrentWheel)
                    race_2.addSemaphore(semaphore, From=True, To=False)

                until.addFunction(self.rope_manager.detachRopeHand)

            with tc.addIfTask(self.wheel_manager.isAllChainsComplete) as (true, _):
                true.addFunction(self._nodeAlphaTo, self.reward_node, 0, 1, 1000)
                true.addFunction(self.enigmaComplete)

    def cleanUpCurrentWheelAndRopeLine(self, cb_get_wheel):
        cur_wheel = cb_get_wheel()

        while cur_wheel is not None:
            wheel = cur_wheel
            cur_wheel = wheel.getPrev()
            rope = wheel.getRope()

            if rope is not None:
                rope_entity_node = rope.getMovie().getEntityNode()

                if rope is not None and rope_entity_node.isActivate() is True:
                    rope.cleanUp()
                    self.rope_manager.deleteRope(rope)
                    wheel.setRope(None)

            wheel.cleanUpNextPrev()

            if wheel.isRoyal() is False:
                wheel_team = wheel.getTeam()
                wheel_movie = wheel.getMovie()
                sprite = self.wheel_manager.getWheelTeamSpriteByTeam(wheel_team)
                EDIT_DISABLE_LAYERS(sprite, False, wheel_movie)
                wheel.setTeam(None)

            self.wheel_manager.cleanWheelValidNeighbours()

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(Counterbalance, self)._onPreparation()
        self._loadParam()
        self._setup()

    def _onActivate(self):
        super(Counterbalance, self)._onActivate()
        self._nodeAlphaTo(self.reward_node, 1, 0, 50)

    def _onDeactivate(self):
        super(Counterbalance, self)._onDeactivate()
        self._cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._runTaskChains()

    def _restoreEnigma(self):
        self._runTaskChains()

    def _resetEnigma(self):
        self._cleanUp()
        self._setup()
        self._runTaskChains()

    def _stopEnigma(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

    def _skipEnigma(self):
        self._cleanUp()
        self._setup()

        skip_wheels_name = self.params.skip_ways
        skip_wheels = dict()

        for team, names in skip_wheels_name.items():
            for name in names:
                team_wheels = skip_wheels.get(team)
                if team_wheels is None:
                    ls = [self.wheel_manager.getWheelByName(name)]
                    skip_wheels[team] = ls
                else:
                    team_wheels.append(self.wheel_manager.getWheelByName(name))
                    skip_wheels[team] = team_wheels

        for wheel_list in skip_wheels.values():
            for index, wheel in enumerate(wheel_list):
                def getWheel():
                    return wheel_list[index]

                def getPrevWheel():
                    return wheel_list[index - 1]

                if index < len(wheel_list) - 1:
                    wheel.setNext(wheel_list[index + 1])

                if index != 0:
                    team = wheel.getPrev().getTeam()

                    if wheel.getTeam() != team:
                        wheel.setTeam(team)

                        sprite = self.wheel_manager.getWheelTeamSpriteByTeam(team)
                        movie = wheel.getMovie()
                        movie.delParam("DisableLayers", sprite)

                    self.rope_manager.updateAttachedRope(getPrevWheel)
                    self.rope_manager.createAndAttachRope(getWheel)

        with TaskManager.createTaskChain(Repeat=False) as tc:
            for wheel_list in skip_wheels.values():
                wheel = wheel_list[-1]
                tc.addScope(wheel.scopePlay)

                while wheel.getPrev() is not None:
                    wheel = wheel.getPrev()
                    tc.addScope(wheel.scopePlay)

        self._nodeAlphaTo(self.reward_node, 0, 1, 1000)

        return
