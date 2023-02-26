from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.System.SystemAchievements import SystemAchievements
from HOPA.System.SystemCollectibles import SystemCollectibles
from HOPA.System.SystemMorphs import SystemMorphs

ALIAS_ENV = ''

TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER = "$AchievementCounter"
TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT = "$AchievementText"

TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_COLLECTIBLE = "ID_ACHIEVEMENT_PLATE_TEXT_FIND_COLLECTIBLE"
TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_ALL_COLLECTIBLES = "ID_ACHIEVEMENT_PLATE_TEXT_FIND_ALL_COLLECTIBLES"
TEXT_ID_ACHIEVEMENT_PLATE_TEXT_COLLECTIBLES_COUNTER = "ID_ACHIEVEMENT_PLATE_COLLECTIBLES_COUNTER"
TEXT_ID_ACHIEVEMENT_PLATE_EMPTY_TEXT = "ID_ACHIEVEMENT_PLATE_TEXT_EMPTY"

TEXT_ID_ACHIEVEMENT_PLATE_TEXT_ACHIEVEMENT_COMPLETE = "ID_ACHIEVEMENT_PLATE_TEXT_ACHIEVEMENT_COMPLETE"
TEXT_ID_ACHIEVEMENT_PLATE_ACHIEVEMENTS_COUNTER = "ID_ACHIEVEMENT_PLATE_ACHIEVEMENTS_COUNTER"

TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_MORPH = "ID_ACHIEVEMENT_PLATE_TEXT_FIND_MORPH"
TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FOUND_ALL_MORPHS = "ID_ACHIEVEMENT_PLATE_TEXT_FOUND_ALL_MORPHS"
TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FOUND_SCENE_MORPHS = "ID_ACHIEVEMENT_PLATE_TEXT_FOUND_SCENE_MORPHS"
TEXT_ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_SCENE = "ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_SCENE"
TEXT_ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_TOTAL = "ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_TOTAL"

ACHIEVEMENT_PLATE_SHOW_DELAY = DefaultManager.getDefaultFloat('AchievementPLateShowDelay', 1500.0)

class PlateSceneEffect(object):
    def __init__(self, movie):
        self.movie = movie
        self.content_slot = self.movie.getMovieSlot('scene_effect')

    def scopePlayEffect(self, source):
        source.addPlay(self.movie, Wait=True)

class AchievementsInGameMenu(BaseEntity):
    semaphore_queue_is_empty = Semaphore(True, 'QueueAchievementPlateIsEmpty')

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "isOpen")

        Type.addAction(Type, "AchievementsQueue", Append=AchievementsInGameMenu.__appendQueue)
        Type.addAction(Type, "CollectiblesQueue", Append=AchievementsInGameMenu.__appendQueue)
        Type.addAction(Type, "MorphsQueue", Append=AchievementsInGameMenu.__appendQueue)

    @staticmethod
    def __appendQueue(*args):
        if AchievementsInGameMenu.semaphore_queue_is_empty.getValue() is False:
            return
        AchievementsInGameMenu.semaphore_queue_is_empty.setValue(False)

    def __init__(self):
        super(AchievementsInGameMenu, self).__init__()
        self.tc_open_close = None
        self.tc_show_plate = None
        self.tc_click_buttons = None

        self.content_plate = None
        self.content_plate_entity_node = None

        self.achievement_movie = None
        self.achievement_movie_node = None
        self.default_movie = None
        self.default_movie_node = None

        self.button_plate = None
        self.button_achievement = None
        self.button_collectibles = None

        self.scene_effect_open = None
        self.scene_effect_close = None

        self.current_scene_effect = None

        self.setup_text_scene_effect_first_part = None
        self.setup_text_scene_effect_second_part = None

        self.semaphore_play_scene_effect = None
        self.counter_node = None

    def _onPreparation(self):
        current_scene = SceneManager.getCurrentSceneName()
        self.semaphore_play_scene_effect = Semaphore(False, "AchievementPlateSceneEffectPlay")

        self.__setupPlate()
        self.__setCollectiblesText(current_scene)  # default text
        if self.isOpen is True:
            self.__setPlate()

    def __setupPlate(self):
        movie_scene_effect_open = self.object.getObject('Movie2_Open')  # first frame is close state
        movie_scene_effect_close = self.object.getObject('Movie2_Close')  # first frame is open state
        self.scene_effect_open = PlateSceneEffect(movie_scene_effect_open)
        self.scene_effect_close = PlateSceneEffect(movie_scene_effect_close)

        self.content_plate = self.object.getObject('Movie2_PlateContent')
        self.content_plate_entity_node = self.content_plate.getEntityNode()

        self.__setCurrentSceneEffect(self.isOpen)

        self.button_plate = self.object.getObject('Movie2Button_Plate')
        button_plate_entity_node = self.button_plate.getEntityNode()
        content_plate_slot_button_plate = self.content_plate.getMovieSlot('plate')
        content_plate_slot_button_plate.addChild(button_plate_entity_node)

        if self.object.hasObject('Movie2Button_Achievements'):
            self.button_achievement = self.object.getObject('Movie2Button_Achievements')
            button_achievement_entity_node = self.button_achievement.getEntityNode()
            content_plate_slot_button_achievement = self.content_plate.getMovieSlot('achievements')
            content_plate_slot_button_achievement.addChild(button_achievement_entity_node)

        if self.object.hasObject('Movie2Button_CollectibleItems'):
            self.button_collectibles = self.object.getObject('Movie2Button_CollectibleItems')
            button_collectibles_entity_node = self.button_collectibles.getEntityNode()
            content_plate_slot_button_collectibles = self.content_plate.getMovieSlot('collectibles')
            content_plate_slot_button_collectibles.addChild(button_collectibles_entity_node)

        self.counter_node = self.content_plate.getMovieText(TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER)

        self.setup_text_scene_effect_first_part = self.object.getObject('Movie2_SetupTextSceneEffectFirstPart')
        self.setup_text_scene_effect_second_part = self.object.getObject('Movie2_SetupTextSceneEffectSecondPart')

        setup_text_scene_effect_first_part_entity_node = self.setup_text_scene_effect_first_part.getEntityNode()
        setup_text_scene_effect_second_part_entity_node = self.setup_text_scene_effect_second_part.getEntityNode()

        slot_setup_text_scene_effect = self.content_plate.getMovieSlot('setup_text_scene_effect')
        slot_setup_text_scene_effect.addChild(setup_text_scene_effect_first_part_entity_node)
        slot_setup_text_scene_effect.addChild(setup_text_scene_effect_second_part_entity_node)

    def __cleanAchievementMovie(self):
        if self.achievement_movie_node is not None:
            self.achievement_movie_node.removeFromParent()
            self.achievement_movie_node = None
        if self.achievement_movie is not None:
            self.achievement_movie.onDestroy()
            self.achievement_movie = None

        if self.default_movie_node is not None:
            self.default_movie_node.removeFromParent()
            self.default_movie_node = None
        if self.default_movie is not None:
            self.default_movie.onDestroy()
            self.default_movie = None

    def __setCurrentSceneEffect(self, state):
        if state is True:
            self.scene_effect_close.movie.setEnable(True)
            self.scene_effect_open.movie.setEnable(False)
            self.current_scene_effect = self.scene_effect_close
        else:
            self.scene_effect_open.movie.setEnable(True)
            self.scene_effect_close.movie.setEnable(False)
            self.current_scene_effect = self.scene_effect_open

        self.content_plate_entity_node.removeFromParent()
        self.current_scene_effect.content_slot.addChild(self.content_plate_entity_node)
        self.object.setParam('isOpen', state)

    def __setCollectiblesText(self, scene_name):
        system_collectibles = SystemManager.getSystem('SystemCollectibles')
        collectibles_on_scene = system_collectibles.getCollectiblesOnScene(scene_name)
        collectible_group = system_collectibles.getCollectibleGroup(scene_name)

        if collectibles_on_scene is not None:
            if collectible_group is None:
                Trace.msg_err("AchievementsInGameMenu in __setCollectiblesText: found collectibles on this "
                              "scene, but no information about them in CollectiblesScene.xlsx. Fix it and try again!")
                complete_counter = None
            else:
                complete_counter = collectible_group.found_collectibles

            number_of_collectibles_on_scene = len(collectibles_on_scene)

            text_id_description = TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_COLLECTIBLE
            if complete_counter == number_of_collectibles_on_scene:
                text_id_description = TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_ALL_COLLECTIBLES

            Mengine.removeTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT)
            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, text_id_description)

            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, TEXT_ID_ACHIEVEMENT_PLATE_TEXT_COLLECTIBLES_COUNTER)
            Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, str(complete_counter), str(number_of_collectibles_on_scene))
            self.__setEnableCounter(True)
        else:
            Mengine.removeTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT)
            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, TEXT_ID_ACHIEVEMENT_PLATE_EMPTY_TEXT)
            self.__setEnableCounter(False)

    def __setEnableCounter(self, state):
        if state is True:
            self.counter_node.enable()
        else:
            self.counter_node.disable()

    def __setAchievementsText(self, achievement_name):
        achievements = SystemAchievements.getAchievements()

        number_of_achievements = len(achievements)
        counter = 0
        for value in achievements.values():
            if value.complete is True:
                counter += 1

        text_id_achievement = SystemAchievements.getAchievement(achievement_name).params.task_id_name

        display_text_achievement_name = Mengine.getTextFromID(str(text_id_achievement))

        Mengine.removeTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT)
        Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, TEXT_ID_ACHIEVEMENT_PLATE_TEXT_ACHIEVEMENT_COMPLETE)
        Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, display_text_achievement_name)

        Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, TEXT_ID_ACHIEVEMENT_PLATE_ACHIEVEMENTS_COUNTER)
        Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, str(counter), str(number_of_achievements))
        self.__setEnableCounter(True)

    def __setMorphsText(self, morph_id=None):
        active_morphs = SystemMorphs.getActiveMorphIDs()
        picked_morphs = SystemMorphs.getPickedMorphIDs()
        scene_morphs = SystemMorphs.getSceneMorphIDs()
        all_morphs = SystemMorphs.getAllMorphIDs()

        Mengine.removeTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT)

        if len(active_morphs) == 0:
            # if player collect all morphs in the game
            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FOUND_ALL_MORPHS)

            self.__setEnableCounter(False)

        elif len(scene_morphs) > 0:
            # if player has morphs to collect on this scene
            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FIND_MORPH)

            if DefaultManager.getDefaultBool("MorphShowCurSceneCounter", False) is True:
                # shows how many morphs on this scene left
                Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, TEXT_ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_SCENE)
                Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, str(len(scene_morphs)), str(len(picked_morphs)), str(len(all_morphs)))
            else:
                # shows only total counter
                Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, TEXT_ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_TOTAL)
                Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, str(len(picked_morphs)), str(len(all_morphs)))

            self.__setEnableCounter(True)

        else:
            # if player collect all morphs on this scene
            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_TEXT, TEXT_ID_ACHIEVEMENT_PLATE_TEXT_FOUND_SCENE_MORPHS)

            Mengine.setTextAlias(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, TEXT_ID_ACHIEVEMENT_PLATE_MORPHS_COUNTER_TOTAL)
            Mengine.setTextAliasArguments(ALIAS_ENV, TEXT_ALIAS_ACHIEVEMENT_PLATE_COUNTER, str(len(picked_morphs)), str(len(all_morphs)))
            self.__setEnableCounter(True)

    def _onActivate(self):
        self.__runTaskChains()

    def __runTaskChains(self):
        self.tc_open_close = TaskManager.createTaskChain(Repeat=True)
        self.tc_show_plate = TaskManager.createTaskChain(Repeat=True)
        self.tc_click_buttons = TaskManager.createTaskChain(Repeat=True)
        self.tc_click_sockets = TaskManager.createTaskChain(Repeat=True)

        with self.tc_open_close as tc_open_close:
            tc_open_close.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_plate)
            tc_open_close.addFunction(self.__setPlate)
            tc_open_close.addScope(self.__scopeSceneEffect)

        with self.tc_show_plate as tc_show_plate:
            tc_show_plate.addFunction(self.__isQueueEmpty)
            tc_show_plate.addSemaphore(self.semaphore_queue_is_empty, From=False)
            tc_show_plate.addScope(self.__scopeShowCompletedTasks)

        with self.tc_click_buttons as tc_click_buttons:
            with tc_click_buttons.addRaceTask(2) as (tc_button_achievement, tc_button_collectibles):
                tc_button_achievement.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_achievement)
                tc_button_achievement.addNotify(Notificator.onBonusSceneTransition, "Achievements")

                tc_button_collectibles.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_collectibles)
                tc_button_collectibles.addNotify(Notificator.onBonusSceneTransition, "Collectibles")

        with self.tc_click_sockets as tc_click_sockets:
            tc_click_sockets.addListener(Notificator.onCloseAchievementPlate)

            with tc_click_sockets.addIfTask(lambda: self.isOpen is True) as (source_true, source_false):
                source_true.addScope(self.__scopeSceneEffect)

    def __getCurrentSceneEffect(self):
        return self.current_scene_effect

    def __scopeSceneEffect(self, source):
        with source.addIfTask(self.semaphore_play_scene_effect.getValue) as (source_true, source_false):
            source_false.addSemaphore(self.semaphore_play_scene_effect, From=False, To=True)
            with GuardBlockInput(source_false) as guard_source:
                guard_source.addScope(self.__getCurrentSceneEffect().scopePlayEffect)
                guard_source.addTask('TaskMovieLastFrame', Movie=self.__getCurrentSceneEffect().movie, Value=False)
                guard_source.addFunction(self.__setCurrentSceneEffect, not self.isOpen)
            source_false.addSemaphore(self.semaphore_play_scene_effect, To=False)

    def __isQueueEmpty(self):
        if self.object.isQueueEmpty() is False:
            self.semaphore_queue_is_empty.setValue(False)
            return True

        self.semaphore_queue_is_empty.setValue(True)
        return False

    def __scopeShowCompletedTasks(self, source):  # by the word Tasks are meant Achievements and Collectibles
        with source.addIfTask(lambda: self.isOpen is False) as (source_for_close, source_for_open):
            source_for_close.addFunction(self.__setPlate)
            source_for_close.addScope(self.__scopeSceneEffect)
            source_for_close.addDelay(ACHIEVEMENT_PLATE_SHOW_DELAY)

            with source_for_close.addIfTask(self.semaphore_play_scene_effect.getValue) as (source_skip, source_close):  # source_skip if we closed plate ourselves
                source_close.addScope(self.__scopeSceneEffect)

                source_skip.addDummy()

            source_for_close.addFunction(self.__setPlate)

            source_for_open.addScope(self.__scopePlaySetTextEffect)

    def __setPlate(self):
        achievement_name = self.object.popParam('AchievementsQueue')

        # show collectibles if we just collected one
        collectible_scene = self.object.popParam("CollectiblesQueue")
        if collectible_scene is None:
            # we should always show collectibles if Morphs disabled (if no achievements)
            if SystemMorphs.isMorphsEnabled() is False:
                collectible_scene = SceneManager.getCurrentSceneName()
            # but if Morphs are enabled, force show collectibles if we in search collectibles mode
            elif SystemCollectibles.isSearchMode() is True:
                collectible_scene = SceneManager.getCurrentSceneName()

        self.__setAchievementMovie(achievement_name, collectible_scene)
        self.__setTexts(achievement_name, collectible_scene)

    def __setAchievementMovie(self, achievement_name=None, collectible_scene=None):
        self.__cleanAchievementMovie()
        if achievement_name is not None:
            achievement_name = achievement_name.replace(' ', '')
            self.achievement_movie = self.object.tryGenerateObjectUnique('Achievement_Movie2', 'Movie2_' + achievement_name, Enable=True)
            if self.achievement_movie is None:
                return

            self.achievement_movie.setEnable(True)
            self.achievement_movie.setLoop(True)
            self.achievement_movie.setPlay(True)
            self.achievement_movie_node = self.achievement_movie.getEntityNode()

            slot_achievement_movie = self.content_plate.getMovieSlot('achievement_movie')
            slot_achievement_movie.addChild(self.achievement_movie_node)
        else:
            if collectible_scene is not None:
                icon_movie = self.object.tryGenerateObjectUnique('Default_Movie2', 'Movie2_Default', Enable=True)
            else:
                icon_movie = self.object.tryGenerateObjectUnique('Morph_Movie2', 'Movie2_Morph', Enable=True)
            self.default_movie = icon_movie

            if self.default_movie is None:
                return

            self.default_movie.setEnable(True)
            self.default_movie.setLoop(True)
            self.default_movie.setPlay(True)
            self.default_movie_node = self.default_movie.getEntityNode()

            slot_default = self.content_plate.getMovieSlot('default')
            slot_default.addChild(self.default_movie_node)

    def __setTexts(self, achievement_name=None, collectible_scene=None):
        """
        :return: True if will showed main info (morphs or collectibles)
                 * main morphs if SystemMorphs.isMorphsEnabled() is True else collectibles
                 False if will showed other (achievements, morphs/collectibles)
        """
        if achievement_name is not None:
            self.__setAchievementsText(achievement_name)
            return False

        if collectible_scene is not None:
            self.__setCollectiblesText(collectible_scene)
            return False

        if SystemMorphs.isMorphsEnabled() is True:
            morph_id = self.object.popParam("MorphsQueue")
            self.__setMorphsText(morph_id)
            return True

        Trace.log("Entity", 0, "AchievementsInGameMenu.__setTexts: No achievement_name or collectible_scene inputted, also Morphs are disabled")

        return False

    def __scopePlaySetTextEffect(self, source):
        source.addEnable(self.setup_text_scene_effect_first_part)
        source.addPlay(self.setup_text_scene_effect_first_part, Wait=True)
        source.addFunction(self.__setPlate)

        source.addDisable(self.setup_text_scene_effect_first_part)

        source.addEnable(self.setup_text_scene_effect_second_part)
        source.addPlay(self.setup_text_scene_effect_second_part, Wait=True)
        source.addDisable(self.setup_text_scene_effect_second_part)

    def _onDeactivate(self):
        self.__cleanUp()

    def __cleanUp(self):
        if self.tc_show_plate is not None:
            self.tc_show_plate.cancel()
        self.tc_show_plate = None

        if self.tc_open_close is not None:
            self.tc_open_close.cancel()
        self.tc_open_close = None

        if self.tc_click_buttons is not None:
            self.tc_click_buttons.cancel()
        self.tc_click_buttons = None

        if self.tc_click_sockets is not None:
            self.tc_click_sockets.cancel()
        self.tc_click_sockets = None

        self.button_plate.getEntityNode().removeFromParent()
        self.button_achievement.getEntityNode().removeFromParent()
        self.button_collectibles.getEntityNode().removeFromParent()
        self.setup_text_scene_effect_first_part.getEntityNode().removeFromParent()
        self.setup_text_scene_effect_second_part.getEntityNode().removeFromParent()

        self.content_plate_entity_node.removeFromParent()

        self.content_plate = None
        self.content_plate_entity_node = None

        self.__cleanAchievementMovie()

        self.button_plate = None
        self.button_achievement = None
        self.button_collectibles = None

        self.scene_effect_open = None
        self.scene_effect_close = None

        self.current_scene_effect = None

        self.setup_text_scene_effect_first_part = None
        self.setup_text_scene_effect_second_part = None

        self.semaphore_play_scene_effect = None