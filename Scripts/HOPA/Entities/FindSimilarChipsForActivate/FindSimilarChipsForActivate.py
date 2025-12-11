from Foundation import Utils
from Foundation.Notificator import Notificator
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.FindSimilarChipsForActivateManager import FindSimilarChipsForActivateManager
from Holder import Holder


Enigma = Mengine.importEntity("Enigma")


class Chip(object):
    def __init__(self, chip_id, movie):
        self.id = chip_id
        self.movie = movie
        self.node = movie.getEntityNode()
        self.selected = False

    def scopeClickDown(self, source):
        source.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName='chip')

    def cleanUp(self):
        if self.node.hasParent():
            self.node.removeFromParent()

        self.movie.onFinalize()
        self.movie.onDestroy()


class Place(object):
    def __init__(self, place_id, movie_idle, movie_fight, movie_death, movie_use, progress_bar, num_of_uses, chip_for_use_id):
        self.id = place_id

        self.movie_idle = movie_idle
        self.movie_fight = movie_fight
        self.movie_death = movie_death
        self.movie_use = movie_use
        self.progress_bar = progress_bar

        self.num_of_need_uses = num_of_uses
        self.num_of_uses = num_of_uses
        self.chip_id = chip_for_use_id

        self.selected_place = None
        self.active = True
        self.setupValueFollower()

    def scopeClickDown(self, source):
        source.addTask("TaskMovie2SocketClick", Movie2=self.movie_fight, SocketName='skeleton')

    def causingDamage(self, source, wait):
        current_progress_bar_value = 100 * (float(self.num_of_need_uses - self.num_of_uses + 1) / float(self.num_of_need_uses))

        source.addFunction(self.__setProgressBarValue, current_progress_bar_value)
        if self.num_of_uses == 1:
            self.active = False
            source.addDisable(self.movie_fight)
            source.addEnable(self.movie_death)
            source.addDisable(self.progress_bar)
            source.addTask('TaskMovie2Play', Movie2=self.movie_death, Wait=wait)
            self.num_of_uses -= 1
            return

        self.num_of_uses -= 1

    def setupValueFollower(self):
        def __update(value, progress_bar):
            progress_bar.setValue(value)

        self.progress_bar_follower = Mengine.createValueFollowerLinear(0.0, 0.05, __update, self.progress_bar)
        self.progress_bar.setEnable(True)  # self.progress_bar.setValue(100)

    def __cleanValueFollower(self):
        if self.progress_bar_follower is not None:
            Mengine.destroyValueFollower(self.progress_bar_follower)
            self.progress_bar_follower = None

    def __setProgressBarValue(self, value):
        # self.progress_bar.setValue(value)
        self.progress_bar_follower.setFollow(value)

    def cleanUp(self):
        self.__cleanValueFollower()
        self.movie_idle.getEntityNode().removeFromParent()
        self.movie_fight.getEntityNode().removeFromParent()
        self.movie_death.getEntityNode().removeFromParent()
        self.progress_bar.getEntityNode().removeFromParent()
        self.progress_bar.onDestroy()


class FindSimilarChipsForActivate(Enigma):
    def __init__(self):
        super(FindSimilarChipsForActivate, self).__init__()
        self.tc = None
        self.semaphore = None
        self.param = None

        self.finish_counter_total = 0
        self.finish_counter_current = 0

        self.places = {}
        self.chips = {}
        self.chips_num = 0

        self.hand_setup_movie = None
        self.hand_charged_movie = None
        self.slots_movie = None

        self.selected_place = None

    @staticmethod
    def declareORM(type_):
        Enigma.declareORM(type_)
        type_.addAction('availablePlaces')

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParam(self):
        self.param = FindSimilarChipsForActivateManager.getParam(self.EnigmaName)

    def _setup(self):
        self.slots_movie = self.object.getObject(self.param.slots)
        self.slots_movie.getSocket('failClick').disable()

        self.hand_setup_movie = self.object.getObject(self.param.hand_setup)
        self.hand_charged_movie = self.object.getObject(self.param.hand_charged)
        available_places = self.object.getParam('availablePlaces')

        for (place_id, (movie_names, num_of_uses, chip_for_use_id)) in self.param.places.iteritems():
            if available_places.get(place_id, None) is None:
                available_places[place_id] = num_of_uses
            slot = self.slots_movie.getMovieSlot('place_{}'.format(place_id))

            movie_idle = self.object.getObject(movie_names[0])
            movie_fight = self.object.getObject(movie_names[1])
            movie_death = self.object.getObject(movie_names[2])
            movie_use = self.object.getObject(movie_names[3])
            progress_bar = self.object.tryGenerateObjectUnique('ProgressBar_{}'.format(place_id), movie_names[4], Enable=True)

            slot.addChild(movie_idle.getEntityNode())
            slot.addChild(movie_fight.getEntityNode())
            slot.addChild(movie_death.getEntityNode())

            pb_slot_name = movie_names[5]
            pb_slot = self.slots_movie.getMovieSlot(pb_slot_name)
            pb_slot.addChild(progress_bar.getEntityNode())

            place = Place(place_id, movie_idle, movie_fight, movie_death, movie_use, progress_bar, num_of_uses, chip_for_use_id)
            self.finish_counter_total += num_of_uses
            self.places[place_id] = place

        self.object.setParam('availablePlaces', available_places)

        for (chip_type_id, (movie_name, num_of_chips)) in self.param.chips.iteritems():
            self.chips_num += num_of_chips
            chip_list = []

            for i in range(1, num_of_chips + 1):
                movie = self.object.tryGenerateObjectUnique('chip_{}_{}'.format(chip_type_id, i), movie_name, Enable=False)
                self.addChild(movie.getEntityNode())

                chip = Chip(i, movie)
                chip_list.append(chip)

            self.chips[chip_type_id] = chip_list

        self.__disableSelectedLayer()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()

        for place in self.places.values():
            place.cleanUp()

        for chip_list in self.chips.values():
            for chip in chip_list:
                chip.cleanUp()

        self.finish_counter_current = 0
        self.finish_counter_total = 0

    def incrementFinishCounterCurrent(self):
        self.finish_counter_current += 1

    # -------------- Scopes ---------------------------------------------------------------------------------------
    def __setSelectedPlace(self, flag):
        self.selected_place = flag

    def __disableSelectedLayer(self):
        for chip_list in self.chips.values():
            for chip in chip_list:
                chip.movie.appendParam('DisableLayers', 'Selected')
                chip.selected = False

    def __scopeDisableChips(self, source):
        for chip_list, parallel_chip_list in source.addParallelTaskList(self.chips.values()):
            for chip, parallel_chip in parallel_chip_list.addParallelTaskList(chip_list):
                parallel_chip.addTask('TaskNodeAlphaTo', Node=chip.node, To=0.0, From=1.0,
                                      Time=self.param.chips_prototypes_alpha)
                parallel_chip.addFunction(chip.movie.appendParam, 'DisableLayers', 'Selected')
                parallel_chip.addDisable(chip.movie)

    def __scopeKillSkeleton(self, source):
        place = self.selected_place

        source.addDisable(place.movie_idle)
        source.addEnable(place.movie_fight)

        source.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=1.0, To=0.0,
                       Time=self.param.hand_charged_alpha_disable)
        source.addDisable(self.hand_charged_movie)

        source.addEnable(place.movie_use)
        source.addTask("TaskNodeAlphaTo", Node=place.movie_use.getEntityNode(), From=0.0, To=1.0,
                       Time=self.param.movie_use_alpha_enable)

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addTask('TaskMovie2Play', Movie2=place.movie_use, Wait=True)
            parallel_1.addTask("TaskNodeAlphaTo", Node=place.movie_use.getEntityNode(), From=1.0, To=0.0,
                               Time=self.param.movie_use_alpha_disable)
            parallel_1.addDisable(place.movie_use)

            parallel_1.addEnable(self.hand_setup_movie)
            parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_setup_movie.getEntityNode(), From=0.0, To=1.0,
                               Time=self.param.hand_setup_alpha_enable)

            parallel_2.addScope(place.causingDamage, True)

            parallel_2.addNotify(Notificator.onSoundEffectOnObject, self.object, 'FindSimilarChipsForActivate_ChipLoss')
            parallel_2.addFunction(self.__disableSelectedLayer)

    def __checkWinComb(self):
        flag = True
        for (chip_list_id, chip_list) in self.chips.iteritems():
            if flag is False:
                break
            if chip_list_id == self.selected_place.chip_id:
                for chip in chip_list:
                    if chip.selected is False:
                        flag = False
                        break
            elif chip_list_id != self.selected_place.chip_id:
                for chip in chip_list:
                    if chip.selected is True:
                        flag = False
                        break
        if flag is False:
            return False
        else:
            return True

    def __scopeResolveClickOnChip(self, source, chip):
        if chip.selected is False:
            chip.selected = True
            source.addFunction(chip.movie.delParam, 'DisableLayers', 'Selected')
        elif chip.selected is True:
            chip.selected = False
            source.addFunction(chip.movie.appendParam, 'DisableLayers', 'Selected')
        if self.__checkWinComb() is True:
            temp_dict = self.object.getParam('availablePlaces')
            if self.selected_place.num_of_uses == 1:
                temp_dict.pop(self.selected_place.id)
            self.object.setParam('availablePlaces', temp_dict)
            source.addScope(self.__scopeDisableChips)
            source.addScope(self.__scopeKillSkeleton)
            source.addFunction(self.incrementFinishCounterCurrent)
            source.addFunction(self.__setSelectedPlace, None)
            source.addSemaphore(self.semaphore, To=True)

    def __scopeFailChipClick(self, source):
        place = self.selected_place
        if place is None:
            return

        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=1.0, To=0.0,
                               Time=self.param.hand_charged_alpha_disable)
            parallel_1.addDisable(self.hand_charged_movie)

            parallel_1.addEnable(self.hand_setup_movie)
            parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_setup_movie.getEntityNode(), From=0.0, To=1.0,
                               Time=self.param.hand_setup_alpha_enable)

            parallel_2.addScope(self.__scopeDisableChips)
            parallel_2.addFunction(self.__disableSelectedLayer)
            parallel_2.addFunction(self.__setSelectedPlace, None)
            parallel_2.addDisable(place.movie_idle)
            parallel_2.addEnable(place.movie_fight)

        source.addSemaphore(self.semaphore, To=True)

    def __scopeHolderClick(self, source, holder, cb_holder_click_resolver, sound):
        holder = holder.get()
        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, sound)
            parallel_2.addScope(cb_holder_click_resolver, holder)

    def __scopeClickOnChip(self, source):
        chip_holder = Holder()
        with source.addRaceTask(2) as (race_1, race_2):
            for chip_list, race in race_1.addRaceTaskList(self.chips.values()):
                for chip, race_chip in race.addRaceTaskList(chip_list):
                    race_chip.addScope(chip.scopeClickDown)
                    race_chip.addFunction(chip_holder.set, chip)

            race_2.addTask('TaskMovie2SocketClick', SocketName='failClick', Movie2=self.slots_movie)
            race_2.addScope(self.__scopeFailChipClick)

        source.addScope(self.__scopeHolderClick, chip_holder, self.__scopeResolveClickOnChip, 'FindSimilarChipsForActivate_ClickOnChip')

    def __scopeSetChipsOnSlots(self, source):
        temp_list = []
        for i in range(1, self.chips_num + 1):
            temp_list.append(i)

        for chip_list in self.chips.values():
            for chip in chip_list:
                el = Utils.rand_element(temp_list)
                slot = self.slots_movie.getMovieSlot('slot_{}'.format(el))
                chip.node.removeFromParent()
                slot.addChild(chip.node)
                temp_list.remove(el)

        for chip_list, parallel in source.addParallelTaskList(self.chips.values()):
            for chip, parallel_chip in parallel.addParallelTaskList(chip_list):
                parallel_chip.addEnable(chip.movie)
                parallel_chip.addTask('TaskNodeAlphaTo', Node=chip.node, To=1.0, From=0.0,
                                      Time=self.param.chips_prototypes_alpha)

    def __checkComplete(self):
        if self.finish_counter_current >= self.finish_counter_total and self.selected_place is None:
            self.tc.cancel()
            self.enigmaComplete()

    def __scopeResolveClickOnPlace(self, source, place):
        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addFunction(self.__setSelectedPlace, place)

            parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_setup_movie.getEntityNode(), From=1.0, To=0.0,
                               Time=self.param.hand_setup_alpha_disable)
            parallel_1.addDisable(self.hand_setup_movie)

            parallel_1.addEnable(self.hand_charged_movie)
            parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=0.0, To=1.0,
                               Time=self.param.hand_charged_alpha_enable)

            parallel_2.addEnable(place.movie_idle)
            parallel_2.addDisable(place.movie_fight)
            with parallel_2.addParallelTask(2) as (set_chips, sound):
                set_chips.addScope(self.__scopeSetChipsOnSlots)
                sound.addNotify(Notificator.onSoundEffectOnObject, self.object,
                                'FindSimilarChipsForActivate_ChipsAppearance')

            parallel_2.addSemaphore(self.semaphore, To=False)

            parallel_2.addFunction(self.slots_movie.getSocket('failClick').enable)

            with parallel_2.addRepeatTask() as (repeat, until):
                repeat.addScope(self.__scopeClickOnChip)
                until.addSemaphore(self.semaphore, From=True)

            parallel_2.addFunction(self.slots_movie.getSocket('failClick').disable)

    def __scopeClickOnPlace(self, source):
        place_holder = Holder()
        temp_list_with_places = []

        temp_list_with_places_indexes = self.object.getParam('availablePlaces').keys()
        for i in temp_list_with_places_indexes:
            temp_list_with_places.append(self.places[i])

        for place, race in source.addRaceTaskList(temp_list_with_places):
            race.addScope(place.scopeClickDown)
            race.addFunction(place_holder.set, place)

        source.addScope(self.__scopeHolderClick, place_holder, self.__scopeResolveClickOnPlace,
                        "FindSimilarChipsForActivate_ClickOnSkeleton")
        source.addFunction(self.__checkComplete)

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def _runTaskChain(self):
        self.semaphore = Semaphore(False, self.EnigmaName)
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self.__scopeClickOnPlace)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(FindSimilarChipsForActivate, self)._onPreparation()
        self._loadParam()

    def _onActivate(self):
        super(FindSimilarChipsForActivate, self)._onActivate()
        self._setup()

    def _onDeactivate(self):
        super(FindSimilarChipsForActivate, self)._onDeactivate()
        self._cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        available_places_id = self.object.getParam('availablePlaces').keys()
        for place in self.places.values():
            place.movie_idle.setEnable(False)
            place.movie_death.setEnable(False)
            place.movie_use.setEnable(False)

            if place.id in available_places_id:
                place.movie_fight.setEnable(True)
            else:
                place.movie_fight.setEnable(False)

        self.hand_charged_movie.setEnable(False)

        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        with TaskManager.createTaskChain() as tc:
            tc.addScope(self.__scopeFailChipClick)

    def _skipEnigmaScope(self, source):
        source.addFunction(self.tc.cancel)
        source.addScope(self.__scopeFailChipClick)

        source.addTask("TaskNodeAlphaTo", Node=self.hand_setup_movie.getEntityNode(), From=1.0, To=0.0,
                       Time=self.param.hand_setup_alpha_disable)
        source.addDisable(self.hand_setup_movie)

        source.addEnable(self.hand_charged_movie)
        source.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=0.0, To=1.0,
                       Time=self.param.hand_charged_alpha_enable)

        for place in set(self.places.values()):
            for _ in range(place.num_of_uses):
                source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'FindSimilarChipsForActivate_ChipLoss')

                source.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=1.0, To=0.0,
                               Time=self.param.hand_charged_alpha_disable)
                source.addDisable(self.hand_charged_movie)

                source.addEnable(place.movie_use)
                source.addTask("TaskNodeAlphaTo", Node=place.movie_use.getEntityNode(), From=0.0, To=1.0,
                               Time=self.param.movie_use_alpha_enable)

                with source.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addTask("TaskMovie2Play", Movie2=place.movie_use, Wait=True)
                    parallel_1.addTask("TaskNodeAlphaTo", Node=place.movie_use.getEntityNode(), From=1.0, To=0.0,
                                       Time=self.param.movie_use_alpha_disable)
                    parallel_1.addDisable(place.movie_use)

                    parallel_1.addEnable(self.hand_charged_movie)
                    parallel_1.addTask("TaskNodeAlphaTo", Node=self.hand_charged_movie.getEntityNode(), From=0.0,
                                       To=1.0, Time=self.param.hand_charged_alpha_enable)

                    parallel_2.addScope(place.causingDamage, True)
