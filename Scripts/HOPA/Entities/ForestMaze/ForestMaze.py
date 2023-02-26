# coding=utf-8
"""
Using in 03_ForrestMG in HolidayFun2
"""
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.ForestMazeManager import ForestMazeManager

import Chips

Enigma = Mengine.importEntity("Enigma")

_CHIP_TYPES = {'Block': Chips.BlockChip, 'Player': Chips.PlayerChip, 'Neutral': Chips.NeutralChip, 'Empty': Chips.EmptyChip, 'Enemy': Chips.EnemyChip, }

_EXTRA_CHIP_PARAMS = {'Player': "PlayerMoveTime", 'Neutral': "NeutralMoveTime", 'Enemy': "RotateTime", }

_AVAILABLE_FOR_MOVE = (Chips.PlayerChip, Chips.NeutralChip)

def getChipClassByType(chip_type):
    return _CHIP_TYPES.get(chip_type)

class ForestMaze(Enigma):
    def __init__(self):
        super(ForestMaze, self).__init__()
        self.tc = None
        self.__finish_place = None
        self.finish_place_glow = None
        self.chips = {}
        self.params = None
        self.content = None
        self.__current_selected_chip = None
        self.player_chip = None
        self.empty_chip = None
        self.enemy_chips = []

    def _playEnigma(self):
        self.__loadPrams()
        self.__setupArt()
        self.__runChipsParamsUnittests()
        self.__runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self.__reset()

    def _skipEnigmaScope(self, skip_source):
        finish_point_place_slot = self.__getPlaceSlot(self.__finish_place)
        with GuardBlockInput(skip_source) as guard_source:
            guard_source.addScope(self.player_chip.scopeMoveTo, self.__finish_place, finish_point_place_slot)

    def _onPreparation(self):
        super(ForestMaze, self)._onPreparation()

    def _onActivate(self):
        super(ForestMaze, self)._onActivate()

    def _onDeactivate(self):
        super(ForestMaze, self)._onDeactivate()
        self.__cleanUp()

    def __runChipsParamsUnittests(self):
        def __run_tests():
            for chip in self.chips.values():
                chip.runChipParamsUnittests()

        if _DEVELOPMENT is True:
            __run_tests()
            return

        try:
            __run_tests()
        except AssertionError:
            self.enigmaComplete()

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.params = None

        for chip in self.chips.values():
            chip.cleanUp()
        self.chips = {}

        if bool(ForestMazeManager.getParam(self.EnigmaName, "DisableFinishGlowAfterReset")) is True:
            # because of https://wonderland-games.atlassian.net/browse/CHA-175
            if self.finish_place_glow is not None:
                self.finish_place_glow.getEntityNode().removeFromParent()

        self.__current_selected_chip = None
        self.player_chip = None
        self.empty_chip = None
        self.enemy_chips = []

    def __loadPrams(self):
        self.params = ForestMazeManager.getParam(self.EnigmaName)
        self.__finish_place = self.params.finish_point

    def __setupArt(self):
        self.content = self.object.getObject('Movie2_Content')

        for place in self.params.places.values():
            chip_id = '{}_{}'.format(place.chip_type, place.place_id)

            movie_chip = self.object.tryGenerateObjectUnique(chip_id, place.movie_prototype_name, Enable=True, Interactive=True)

            slot = self.content.getMovieSlot(place.place_id)
            slot.addChild(movie_chip.getEntityNode())

            chip_class = getChipClassByType(place.chip_type)

            extra_param = _EXTRA_CHIP_PARAMS.get(place.chip_type, None)
            if extra_param is not None:
                extra_param = ForestMazeManager.getParam(self.EnigmaName, extra_param)
                chip = chip_class(chip_id, place.place_id, movie_chip, extra_param)
            else:
                chip = chip_class(chip_id, place.place_id, movie_chip)

            chip.createSupportMovies(self, place)

            if isinstance(chip, Chips.PlayerChip):
                self.player_chip = chip

            if isinstance(chip, Chips.EmptyChip):
                self.empty_chip = chip

            if isinstance(chip, Chips.EnemyChip):
                self.enemy_chips.append(chip)

            self.chips[chip_id] = chip

        if self.object.hasObject("Movie2_FinishPlaceGlow") is False:
            if _DEVELOPMENT is True:
                Trace.log("Object", 1, "Object {} don`t have movie for select finish point"
                                       "\nNow finish place don`t select"
                                       "\nIf you want select finish place - "
                                       "add movie Movie2_FinishPlaceGlow to PSD".format(self.object.getName()))
            return

        self.__setupFinishGlow()

    def __setupFinishGlow(self):
        if self.finish_place_glow is None:
            if self.object.hasObject("Movie2_FinishPlaceGlow") is False:
                Trace.log("Entity", 0, "ForestMaze.__setupFinishGlow: can't find 'Movie2_FinishPlaceGlow' with ptc...")
                return
            self.finish_place_glow = self.object.getObject("Movie2_FinishPlaceGlow")

        if self.isPlay() is False:
            self.finish_place_glow.setEnable(False)
            return
        else:
            self.finish_place_glow.setEnable(True)

            finish_slot = self.content.getMovieSlot(self.__finish_place)
            finish_slot_wp = finish_slot.getWorldPosition()
            finish_place_glow_en = self.finish_place_glow.getEntityNode()
            finish_place_glow_en.setWorldPosition(finish_slot_wp)

    def __runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        holder_click = Holder()

        with self.tc as tc:
            for chip, race_source in tc.addRaceTaskList(self.chips.values()):
                race_source.addScope(chip.scopeClick)
                race_source.addFunction(holder_click.set, chip)

            def resolve_holder_click(source, holder):
                clicked_chip = holder.get()
                source.addScope(self.__scopeResolveClickOnChip, clicked_chip)

            tc.addScope(resolve_holder_click, holder_click)
            tc.addScope(self.__scopeTryDeathByEnemy)
            tc.addFunction(self.__checkComplete)

    def __setCurrentSelectedChip(self, chip):
        self.__current_selected_chip = chip

    def __getCurrentSelectedChip(self):
        return self.__current_selected_chip

    def __isNearbyToEmpty(self, chip):
        chip_en = chip.movie_chip.getEntityNode()
        screen_position = Mengine.getNodeScreenPosition(chip_en)

        hotspots_names = Mengine.pickAllHotspot(screen_position)
        nearby_socket = self.empty_chip.movie_chip.getSocket("nearby")

        if nearby_socket in hotspots_names:
            return True
        return False

    def __getNearbyToEmptyChipsList(self):
        resolution = Mengine.getContentResolution()
        resolution_vec2f = Mengine.vec2f(resolution.getWidth(), resolution.getHeight())

        nearby_socket = self.empty_chip.movie_chip.getSocket("nearby")
        nearby_chips = []
        for chip in self.chips.values():
            if not isinstance(chip, _AVAILABLE_FOR_MOVE):
                continue

            chip_en = chip.movie_chip.getEntityNode()

            screen_position = Mengine.getNodeScreenPosition(chip_en)

            hotspots_names = Mengine.pickAllHotspot(screen_position)
            if nearby_socket not in hotspots_names:
                # print chip.chip_id, 'is not nearby to empty'
                continue
            # print chip.chip_id, 'is nearby to empty'
            nearby_chips.append(chip)
        return nearby_chips

    def __scopeResolveClickOnChip(self, source, chip):
        current_chip = self.__getCurrentSelectedChip()

        if not isinstance(chip, Chips.EmptyChip):
            if not isinstance(chip, _AVAILABLE_FOR_MOVE):
                source.addDummy()
                return

            if self.__isNearbyToEmpty(chip) is not True:
                source.addDummy()
                return

            if current_chip is None:
                source.addScope(chip.scopeSelect)
                source.addFunction(self.__setCurrentSelectedChip, chip)
                return

            if current_chip is chip:
                source.addScope(chip.scopeDeselect)
                source.addFunction(self.__setCurrentSelectedChip, None)
                return

            if current_chip is not chip:
                with source.addParallelTask(2) as (select_new, deselect_old):
                    select_new.addScope(chip.scopeSelect)
                    source.addFunction(self.__setCurrentSelectedChip, chip)

                    deselect_old.addScope(current_chip.scopeDeselect)
                return
            return

        if current_chip is None:
            source.addScope(chip.scopeFailClick)
            return

        if isinstance(current_chip, Chips.PlayerChip):
            source.addScope(self.__scopeReplacePlayerChip, chip)
        elif isinstance(current_chip, Chips.NeutralChip):
            source.addScope(self.__scopeReplaceNeutralChip, chip)
        else:
            Trace.log("Manager", 0, "Chip is not Player or Neutral")

    def __getPlaceSlot(self, place_id):
        if _DEVELOPMENT is True:
            assert isinstance(place_id, str) is True

        return self.content.getMovieSlot(place_id)

    def __scopeReplacePlayerChip(self, source, empty_chip):
        if _DEVELOPMENT is True:
            assert isinstance(empty_chip, Chips.EmptyChip) is True

        current_chip = self.__getCurrentSelectedChip()
        current_chip_place_slot_id = current_chip.getPlaceID()
        current_chip_place_slot = self.__getPlaceSlot(current_chip_place_slot_id)

        empty_chip_place_id = empty_chip.getPlaceID()
        empty_chip_place_slot = self.__getPlaceSlot(empty_chip_place_id)

        with GuardBlockInput(source) as guard_source:
            guard_source.addScope(current_chip.scopeDeselect)
            guard_source.addFunction(self.__setCurrentSelectedChip, None)

            guard_source.addScope(current_chip.scopeMoveTo, empty_chip_place_id, empty_chip_place_slot)
            guard_source.addFunction(empty_chip.setOnNewPlace, current_chip_place_slot_id, current_chip_place_slot)

    def __scopeReplaceNeutralChip(self, source, empty_chip):
        if _DEVELOPMENT is True:
            assert isinstance(empty_chip, Chips.EmptyChip) is True

        current_chip = self.__getCurrentSelectedChip()
        current_chip_place_slot_id = current_chip.getPlaceID()
        current_chip_place_slot = self.__getPlaceSlot(current_chip_place_slot_id)

        empty_chip_place_id = empty_chip.getPlaceID()
        empty_chip_place_slot = self.__getPlaceSlot(empty_chip_place_id)

        with GuardBlockInput(source) as guard_source:
            guard_source.addScope(current_chip.scopeDeselect)
            guard_source.addFunction(self.__setCurrentSelectedChip, None)

            guard_source.addScope(current_chip.scopeMoveTo, empty_chip_place_id, empty_chip_place_slot)
            guard_source.addFunction(empty_chip.setOnNewPlace, current_chip_place_slot_id, current_chip_place_slot)
            guard_source.addScope(self.__scopeRotateEnemyChip)

    def __scopeRotateEnemyChip(self, source):
        with GuardBlockInput(source) as guard_source:
            for enemy, parallel in guard_source.addParallelTaskList(self.enemy_chips):
                # parallel.addScope(enemy.scopeRotateChip, self.params.enemy_rotate_angle)
                parallel.addScope(enemy.scopeRotateChip, int(self.params.enemy_rotate_angle))

    def __checkComplete(self):
        if self.player_chip.place_id == self.__finish_place:
            self.enigmaComplete()

    def __scopeTryDeathByEnemy(self, source):
        enemy = self.__checkDeathByEnemy()

        if enemy is None:
            source.addDummy()
            return

        source.addScope(enemy.scopePlayAttackMovie)
        source.addFunction(self.__reset)

    def __checkDeathByEnemy(self):
        chip_en = self.player_chip.movie_chip.getEntityNode()

        screen_position = Mengine.getNodeScreenPosition(chip_en)

        hotspots_names = Mengine.pickAllHotspot(screen_position)

        for enemy in self.enemy_chips:
            nearby_socket = enemy.movie_chip.getSocket("observed_area")
            if nearby_socket not in hotspots_names:
                continue

            return enemy

    def __reset(self):
        self.__cleanUp()
        self.__loadPrams()
        self.__setupArt()
        self.__runTaskChain()