from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.TurnBasedStrategyGoManager import TurnBasedStrategyGoManager

TEXT_EMPTY = 'ID_EMPTY'
TEXT_WIN = 'ID_GO_RESULTS_WIN'
TEXT_LOSE = 'ID_GO_RESULTS_LOSE'
TEXT_ENEMY_COUNTER = 'ID_GO_ENEMY_COUNTER'
TEXT_PLAYER_COUNTER = 'ID_GO_PLAYER_COUNTER'
ALIAS_ENEMY_COUNTER = '$GoEnemyCounter'
ALIAS_PLAYER_COUNTER = '$GoPlayerCounter'
ALIAS_RESULTS = '$GoResults'

Enigma = Mengine.importEntity("Enigma")

class Chip(object):
    def __init__(self, chip_id, movie_chip, owner, place):
        self.chip_id = chip_id
        self.owner = owner
        self.movie_chip = movie_chip
        self.current_place = place
        self.chip_glow = None

    def setCurrentPlace(self, place):
        self.current_place = place

    def scopeChipClick(self, source):
        source.addTask('TaskMovie2SocketClick', Movie2=self.movie_chip, SocketName='socket')

    def enableChipGlow(self, generating_parent):
        self.chip_glow = generating_parent.tryGenerateObjectUnique('ChipGlow', 'Movie2_LightSelected', Enable=True)
        self.movie_chip.getEntityNode().addChild(self.chip_glow.getEntityNode())

    def disableChipGlow(self):
        if self.chip_glow is not None:
            self.chip_glow.removeFromParent()
            self.chip_glow.onDestroy()
            self.chip_glow = None

    def cleanUp(self):
        self.current_place.setOwner(None)
        self.setCurrentPlace(None)
        self.disableChipGlow()
        self.movie_chip.onDestroy()

class Place(object):
    def __init__(self, place_id, movie_place):
        self.place_id = place_id
        self.chip_owner = None  # None
        self.is_glowing = None
        self.movie_place = movie_place
        self.disableGlows()

    def setOwner(self, chip_owner):
        """
        :param chip_owner: None, Enemy or Player
        :return:
        """
        self.chip_owner = chip_owner

    def enableGlow(self, glow_level):
        self.disableGlows()
        self.is_glowing = True

        glow_layer_name = 'glow_level_{}'.format(glow_level)
        if glow_layer_name in self.movie_place.getParam('DisableLayers'):
            self.movie_place.delParam('DisableLayers', glow_layer_name)

    def disableGlows(self):
        self.is_glowing = False
        self.movie_place.appendParam('DisableLayers', 'glow_level_1')
        self.movie_place.appendParam('DisableLayers', 'glow_level_2')

    def scopePlaceClick(self, source):
        source.addTask('TaskMovie2SocketClick', Movie2=self.movie_place, SocketName='socket')

    def cleanUp(self):
        self.movie_place.onDestroy()

class Counter(object):
    def __init__(self, id_, movie, value, text_alias):
        self.id = id_
        self.movie = movie
        self.value = value

        self.text_alias = text_alias

    def updateValue(self, value):
        self.value = value
        Mengine.setTextAliasArguments('', self.text_alias, value)

    def cleanUp(self):
        self.movie.onDestroy()
        Mengine.setTextAliasArguments('', self.text_alias, '')

class TurnBasedStrategyGo(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "NotCompleteLevels")
        Type.addAction(Type, "CurrentLevel")

    def __init__(self):
        super(TurnBasedStrategyGo, self).__init__()
        self.params = None
        self.movie_content = None
        self.chip_counter = 0

        self.places = {}
        self.places_neighbours = {}
        self.enemy_chips = {}
        self.player_chips = {}
        self.selected_chip = None
        self.first_line_places = []
        self.second_line_places = []

        self.enemy_counter = None
        self.player_counter = None

        self.steps = 0
        self.tc = None

    def _onPreparation(self):
        super(TurnBasedStrategyGo, self)._onPreparation()
        self.__loadParam()
        Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_EMPTY)
        Mengine.setTextAlias("", ALIAS_ENEMY_COUNTER, TEXT_EMPTY)
        Mengine.setTextAlias("", ALIAS_PLAYER_COUNTER, TEXT_EMPTY)

    def _onActivate(self):
        super(TurnBasedStrategyGo, self)._onActivate()

    def _onDeactivate(self):
        super(TurnBasedStrategyGo, self)._onDeactivate()

    def __loadParam(self):
        self.params = TurnBasedStrategyGoManager.getParams(self.EnigmaName)
        if self.CurrentLevel is not None and len(self.NotCompleteLevels) == 0:
            return

        self.object.setParam("NotCompleteLevels", self.params.keys())
        self.object.setParam("CurrentLevel", self.NotCompleteLevels[0])

    def __setupLevel(self):
        level_params = self.params.get(self.CurrentLevel)

        self.movie_content = self.object.getObject(level_params.content_name)
        self.__setCounters()
        self.__createPlaces(level_params)

    def __createPlaces(self, level_params):
        places_number = level_params.place_number
        for i in range(1, places_number + 1):
            place_movie_object_name = "Place{}_Level_{}".format(i, level_params.level_id)
            movie_place = self.object.tryGenerateObjectUnique(place_movie_object_name, "Movie2_Place", Enable=True)

            movie_place_en = movie_place.getEntityNode()
            demon_en = self.object.getEntityNode()
            demon_en.addChild(movie_place_en)

            slot = self.movie_content.getMovieSlot('place_{}'.format(i))
            movie_place_en.setWorldPosition(slot.getWorldPosition())
            place = Place(i, movie_place)
            self.places[i] = place

        for i in level_params.start_enemy_slots:
            self.__createChip('Enemy', self.places.get(i))

        for i in level_params.start_players_slots:
            self.__createChip('Player', self.places.get(i))

    def __createChip(self, owner, place):
        if owner not in ['Enemy', 'Player']:
            return

        movie_name = 'Movie2_EnemyChip' if owner == 'Enemy' else 'Movie2_PlayerChip'

        chip_id = 'Chip_{}_{}'.format(owner, self.chip_counter)
        self.chip_counter += 1

        movie_chip = self.object.tryGenerateObjectUnique(chip_id, movie_name, Enable=True)

        movie_chip_en = movie_chip.getEntityNode()
        self.object.getEntityNode().addChild(movie_chip_en)

        place_wp = place.movie_place.getEntityNode().getWorldPosition()
        movie_chip_en.setWorldPosition(place_wp)

        chips = self.enemy_chips if owner == 'Enemy' else self.player_chips
        counter = self.enemy_counter if owner == 'Enemy' else self.player_counter

        chip = Chip(chip_id, movie_chip, owner, place)
        place.setOwner(chip)

        chips[chip_id] = chip

        counter.updateValue(len(chips))
        return chip

    def __setChipMovieToUpperLayer(self, chip):
        en = chip.movie_chip.getEntityNode()
        parent = en.getParent()
        en.removeFromParent()
        parent.addChild(en)

    def __setCounters(self):
        slot_enemy_counter = self.movie_content.getMovieSlot('enemy_counter')
        slot_player_counter = self.movie_content.getMovieSlot('player_counter')

        movie_enemy_counter = self.object.tryGenerateObjectUnique('EnemyCounter', 'Movie2_EnemyChip', Enable=True)
        movie_player_counter = self.object.tryGenerateObjectUnique('EnemyCounter', 'Movie2_PlayerChip', Enable=True)

        slot_enemy_counter.addChild(movie_enemy_counter.getEntityNode())
        slot_player_counter.addChild(movie_player_counter.getEntityNode())

        Mengine.setTextAlias('', ALIAS_ENEMY_COUNTER, TEXT_ENEMY_COUNTER)
        Mengine.setTextAlias('', ALIAS_PLAYER_COUNTER, TEXT_PLAYER_COUNTER)

        self.enemy_counter = Counter('Enemy', movie_enemy_counter, 0, ALIAS_ENEMY_COUNTER)
        self.player_counter = Counter('Player', movie_player_counter, 0, ALIAS_PLAYER_COUNTER)

    def __runTaskChains(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        self.semaphore_player_finish_step = Semaphore(False, 'PlayerFinishStep')
        self.semaphore_enemy_finish_step = Semaphore(False, 'EnemyFinishStep')

        with self.tc as tc:
            tc.addScope(self.__scopePlayersStep)

            tc.addScope(self.__scopeClearSelectedPlaces)
            tc.addScope(self.__checkLevelComplete)

            with tc.addRepeatTask() as (tc_repeat_enemy, tc_until_enemy):
                tc_repeat_enemy.addScope(self.__scopeEnemyAttack)

                tc_until_enemy.addSemaphore(self.semaphore_enemy_finish_step, From=True, To=False)

            tc.addFunction(self.__selectChip, None)
            tc.addScope(self.__scopeClearSelectedPlaces)
            tc.addScope(self.__checkLevelComplete)

    def __scopePlayersStep(self, source):
        source.addScope(self.__scopeCheckStepBlock, owner='Player')
        source.addScope(self.__scopeSelectChipAndMove)
        self.player_counter.updateValue(len(self.player_chips))
        delay = 500
        source.addDelay(delay)

    def __scopeSelectChipAndMove(self, source):
        click_holder = Holder()

        with source.addRepeatTask() as (repeat, until):
            repeat.addScope(self.__scopeSelectOrMove, click_holder)
            until.addSemaphore(self.semaphore_player_finish_step, From=True, To=False)

    def __scopeSelectOrMove(self, source, click_holder):
        with source.addRaceTask(2) as (select, move):
            for chip, race_click in select.addRaceTaskList(self.player_chips.values()):
                race_click.addScope(chip.scopeChipClick)
                race_click.addFunction(self.__disableSelectedChipGlow)
                race_click.addFunction(click_holder.set, chip)

            move.addScope(self.__scopeResolveClickOnChip, click_holder)
            move.addSemaphore(self.semaphore_player_finish_step, From=True)

    def __scopeEnemyAttack(self, source):
        source.addScope(self.__scopeCheckStepBlock, owner='Enemy')

        self.places_neighbours = {}

        if self.steps % 2 == 0:
            value = True
        else:
            value = False
        if self.steps <= 3:
            value = True

        if value is False:
            enemy_chip = self.__getRandomEnemy()
            source.addScope(self.__scopeEnemyCaptureRandomPlace, enemy_chip)
        else:
            source.addFunction(self.__smartStep)
            source.addScope(self.__scopeEnemyRelativelySmartStep)

        for chip in self.enemy_chips.values():
            chip.disableChipGlow()
        self.enemy_counter.updateValue(len(self.enemy_chips))
        self.steps += 1

    def __smartStep(self):
        for chip in self.enemy_chips.values():
            fl, sl = self.__getFirstAndSecondLinePlaces(chip.current_place)

            places = fl + sl

            for place in places:
                if place.chip_owner is not None:
                    continue
                fl_players_places, sl_players_places = self.__getFirstAndSecondLinePlaces(place)
                counter = 0
                captured = 0
                for player_chip in self.player_chips.values():
                    if player_chip.current_place in fl_players_places:
                        counter += 1
                        captured += 1
                        if captured == len(self.player_chips):
                            self.places_neighbours[(place, chip)] = 1000
                            break
                if place in fl:
                    counter += 1

                self.places_neighbours[(place, chip)] = counter + captured

    def __scopeEnemyRelativelySmartStep(self, source):
        place_with_max_neighbours, enemy_chip = max(self.places_neighbours, key=self.places_neighbours.get)
        fl, sl = self.__getFirstAndSecondLinePlaces(enemy_chip.current_place)

        self.__enableGlows(enemy_chip)

        with source.addIfTask(lambda: place_with_max_neighbours in fl) as (true, false):
            true.addScope(self.__scopeDuplicateChip, enemy_chip, place_with_max_neighbours)
            false.addScope(self.__scopeMoveChip, enemy_chip, place_with_max_neighbours)

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addScope(self.__retakeAroundChips, place_with_max_neighbours)
            parallel_2.addScope(self.__scopeDisableAllGlows)
        source.addSemaphore(self.semaphore_enemy_finish_step, To=True)

    def __scopeEnemyCaptureRandomPlace(self, source, chip):
        if len(self.first_line_places) == 0 and len(self.second_line_places) == 0:
            source.addScope(self.__scopeDisableAllGlows)
            return

        random_line_choice = Mengine.rand(2)  # random choice first or second line

        if random_line_choice == 0 and len(self.first_line_places) != 0:
            ind = Mengine.rand(len(self.first_line_places))
            place = self.first_line_places[ind]
            source.addScope(self.__scopeDuplicateChip, chip, place)
            source.addScope(self.__retakeAroundChips, place)
            source.addSemaphore(self.semaphore_enemy_finish_step, To=True)
            return

        if len(self.second_line_places) == 0:
            source.addScope(self.__scopeDisableAllGlows)
            return

        ind = Mengine.rand(len(self.second_line_places))
        place = self.second_line_places[ind]

        source.addScope(self.__scopeMoveChip, chip, place)
        source.addScope(self.__retakeAroundChips, place)
        source.addScope(self.__scopeDisableAllGlows)
        source.addSemaphore(self.semaphore_enemy_finish_step, To=True)

    def __getRandomEnemy(self):
        self.__disableSelectedChipGlow()
        enemy = None
        enemy_chips = self.enemy_chips.values()
        while len(enemy_chips) > 0:
            ind = Mengine.rand(len(enemy_chips))

            enemy = enemy_chips[ind]

            if len(self.second_line_places) == 0 and len(self.first_line_places) == 0:
                # self.__disableAllGlows()
                enemy_chips.remove(enemy)
                continue

            self.__enableGlows(enemy)
            self.__selectChip(enemy)
            return enemy

        return enemy

    def __selectChip(self, chip):
        self.selected_chip = chip

    def __getSelectedChip(self):
        return self.selected_chip

    def __scopeResolveClickOnChip(self, source, click_holder):
        chip = click_holder.get()
        if chip is None:
            return

        source.addFunction(self.__selectChip, chip)
        source.addScope(self.__scopeClearSelectedPlaces)
        source.addFunction(self.__enableGlows, chip)
        source.addScope(self.__scopeSelectNewPlace, chip)

    def __scopeSelectNewPlace(self, source, chip):
        if len(self.first_line_places) == 0 and len(self.second_line_places) == 0:
            source.addScope(self.__scopeDisableAllGlows)
            return

        with source.addRaceTask(2) as (source_first_line, source_second_line):
            if len(self.first_line_places) == 0:
                source_first_line.addBlock()
            for place, fl_place_race in source_first_line.addRaceTaskList(self.first_line_places):
                fl_place_race.addScope(place.scopePlaceClick)
                fl_place_race.addScope(self.__scopeDuplicateChip, chip, place)
                fl_place_race.addScope(self.__retakeAroundChips, place)
                fl_place_race.addScope(self.__scopeDisableAllGlows)

            if len(self.second_line_places) == 0:
                source_second_line.addBlock()
            for place, sl_place_race in source_second_line.addRaceTaskList(self.second_line_places):
                sl_place_race.addScope(place.scopePlaceClick)
                sl_place_race.addScope(self.__scopeMoveChip, chip, place)
                sl_place_race.addScope(self.__retakeAroundChips, place)
                sl_place_race.addScope(self.__scopeDisableAllGlows)

        source.addSemaphore(self.semaphore_player_finish_step, To=True)

    def __scopeDuplicateChip(self, source, chip, place):
        new_chip = self.__createChip(chip.owner, chip.current_place)

        source.addScope(self.__scopeMoveChip, new_chip, place)
        source.addFunction(chip.current_place.setOwner, chip)

    def __scopeMoveChip(self, source, chip, place):
        self.__disableSelectedChipGlow()
        self.__setChipMovieToUpperLayer(chip)
        place_wp = place.movie_place.getEntityNode().getWorldPosition()
        moving_time = 1000  # todo: must be in defaults

        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (move, sound):
                move.addTask("AliasObjectMoveTo", Object=chip.movie_chip, To=(place_wp.x, place_wp.y), Time=moving_time, Wait=True)
                sound.addNotify(Notificator.onSoundEffectOnObject, self.object, "TurnBasedStrategyGo_Move")
            guard_source.addFunction(chip.current_place.setOwner, None)
            guard_source.addFunction(place.setOwner, chip)
            guard_source.addFunction(chip.setCurrentPlace, place)

    def __disableSelectedChipGlow(self):
        if self.__getSelectedChip() is not None:
            self.__getSelectedChip().disableChipGlow()

    def __disableIfGlowing(self, place):
        if place.is_glowing:
            place.disableGlows()

    def __scopeDisableAllGlows(self, source):
        self.__disableSelectedChipGlow()
        places_values = self.places.values()
        for place, parallel_source in source.addParallelTaskList(places_values):
            parallel_source.addFunction(self.__disableIfGlowing, place)

    def __scopeClearSelectedPlaces(self, source):
        self.first_line_places = []
        self.second_line_places = []
        source.addScope(self.__scopeDisableAllGlows)

    def __enableGlows(self, chip):
        if chip == self.selected_chip:
            chip.enableChipGlow(self.object)

        first_line_places, second_line_places = self.__getFirstAndSecondLinePlaces(chip.current_place)

        for fl_place in first_line_places:
            if fl_place.chip_owner is not None:
                continue
            fl_place.enableGlow(1)
            self.first_line_places.append(fl_place)

        for sl_place in second_line_places:
            if sl_place.chip_owner is not None:
                continue
            sl_place.enableGlow(2)
            self.second_line_places.append(sl_place)

    def __scopeCheckStepBlock(self, source, owner):
        if owner not in ['Enemy', 'Player']:
            source.addDummy()
            return
        if owner == 'Player':
            chips = self.player_chips
            player_step = True
        else:
            chips = self.enemy_chips
            player_step = False

        free_fl = []
        free_sl = []
        for chip in chips.itervalues():
            first_line_places, second_line_places = self.__getFirstAndSecondLinePlaces(chip.current_place)

            for fl_place in first_line_places:
                if fl_place.chip_owner is not None:
                    continue
                free_fl.append(fl_place)

            for sl_place in second_line_places:
                if sl_place.chip_owner is not None:
                    continue
                free_sl.append(sl_place)

        if len(free_fl) == 0 and len(free_sl) == 0:
            textField = self.movie_content.getMovieText(ALIAS_RESULTS)
            source.addTask("TaskNodeAlphaTo", Node=textField, From=0.0, To=1.0, Time=500.0)
            source.addDelay(2000)
            if player_step:  # lose
                Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_LOSE)
                source.addFunction(self._resetEnigma)
            else:  # win
                Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_WIN)
                self.object.delParam("NotCompleteLevels", self.CurrentLevel)
                source.addFunction(self.__completeEnigma)

    def __popEnemyChipAndCreateOur(self, fl_place, place, chip):
        if fl_place.chip_owner is None or fl_place.chip_owner.owner == place.chip_owner.owner:
            return
        if chip.owner == 'Player':
            other_chip = self.enemy_chips.pop(fl_place.chip_owner.chip_id)
        else:
            other_chip = self.player_chips.pop(fl_place.chip_owner.chip_id)

        other_chip.cleanUp()

        self.__createChip(chip.owner, fl_place)

    def __retakeAroundChips(self, source, place):
        chip = place.chip_owner
        first_line_places, _ = self.__getFirstAndSecondLinePlaces(place)

        for fl_place, parallel_source in source.addParallelTaskList(first_line_places):
            parallel_source.addFunction(self.__popEnemyChipAndCreateOur, fl_place, place, chip)

    def __getFirstAndSecondLinePlaces(self, current_place):
        def get_resolution_position(place_wp):
            resolution = Mengine.getContentResolution()
            resolution_vec2f = Mengine.vec2f(resolution.getWidth(), resolution.getHeight())
            place_wp_vec2f = Mengine.vec2f(place_wp[0], place_wp[1])

            return place_wp_vec2f / resolution_vec2f

        first_line_socket = self.movie_content.getSocket('first_line_{}'.format(current_place.place_id))
        second_line_socket = self.movie_content.getSocket('second_line_{}'.format(current_place.place_id))
        first_line_places = []
        second_line_places = []
        for place in self.places.values():
            movie_place_node = place.movie_place.getEntityNode()

            screen_position = Mengine.getNodeScreenPosition(movie_place_node)

            hotspots_names = Mengine.pickAllHotspot(screen_position)

            if second_line_socket in hotspots_names:
                if first_line_socket in hotspots_names:
                    first_line_places.append(place)
                else:
                    second_line_places.append(place)

        return first_line_places, second_line_places

    def _isLoseByCount(self):
        if len(self.player_chips) >= len(self.enemy_chips):
            return False
        return True

    def __checkLevelComplete(self, source):
        if len(self.enemy_chips) != 0 and len(self.player_chips) != 0:
            for place in self.places.values():
                if place.chip_owner is None:
                    source.addDummy()
                    return

        textField = self.movie_content.getMovieText(ALIAS_RESULTS)
        source.addTask("TaskNodeAlphaTo", Node=textField, From=0.0, To=1.0, Time=500.0)
        source.addDelay(50)

        if self._isLoseByCount() is True:
            Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_LOSE)
            source.addFunction(self._resetEnigma)
            return
        else:
            Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_WIN)
            source.addFunction(self.__completeEnigma)
            """# self.object.delParam("NotCompleteLevels", self.CurrentLevel)
            source.addScope(self.__checkComplete)

            self.object.setParam("CurrentLevel", self.NotCompleteLevels[0])
            self.__cleanUp()
            self.__setupLevel()
            """
        return

    def __checkComplete(self, source):
        # if len(self.NotCompleteLevels) != 0:
        #    return

        source.addDelay(1000)
        self.__completeEnigma()

    def __completeEnigma(self):
        self.enigmaComplete()
        self.__cleanUp()

        return True

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for obj in self.places.values() + self.enemy_chips.values() + self.player_chips.values() + [self.enemy_counter, self.player_counter]:
            if obj is None:
                continue
            obj.cleanUp()

        self.places = {}
        self.enemy_chips = {}
        self.player_chips = {}
        self.steps = 0

    def _playEnigma(self):
        self.__setupLevel()
        self.__runTaskChains()

    def _restoreEnigma(self):
        self._resetEnigma()

    def _resetEnigma(self):
        self.__cleanUp()
        self._playEnigma()
        Mengine.setTextAlias("", ALIAS_RESULTS, TEXT_EMPTY)

    def _skipEnigmaScope(self, skip_source):
        return