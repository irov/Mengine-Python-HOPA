from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SystemManager import SystemManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

FADE_TIME = DefaultManager.getDefaultFloat("CollectiblesSceneTextFade", 300.0)
ALIAS_COUNT = '$AliasCollectiblesCount'
TEXT_ID_COUNT = 'ID_COLLECTIBLES_COUNT'

class CollectibleInfoPlate(object):
    def __init__(self, button_plate, movie_plate_content, movie_open, movie_close):
        self.button_plate = button_plate
        self.movie_plate_content = movie_plate_content
        self.movie_open = movie_open
        self.movie_close = movie_close

        self.en_movie_plate_content = movie_plate_content.getEntityNode()
        self.movie_open_slot = movie_open.getMovieSlot('scene_effect')
        self.movie_close_slot = movie_close.getMovieSlot('scene_effect')

        self.__tcs = []

        movie_plate_content.getMovieSlot('plate').addChild(button_plate.getEntityNode())

        self.movie_open.setLastFrame(False)
        self.movie_open_slot.addChild(self.en_movie_plate_content)

    def runPlateEffectTC(self):
        tc_enter_listener = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_enter_listener)

        tc_leave_listener = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_leave_listener)

        tc_click_listener = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_click_listener)

        tc_main = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_main)

        semaphore = Semaphore(False, "CollectiblePlateInfo")

        with tc_enter_listener as tc:
            tc.addTask("TaskMovie2ButtonEnter", Movie2Button=self.button_plate, isMouseEnter=False)
            tc.addSemaphore(semaphore, To=True)

        with tc_leave_listener as tc:
            tc.addTask("TaskMovie2ButtonLeave", Movie2Button=self.button_plate, isMouseLeave=False)
            tc.addSemaphore(semaphore, To=False)

        with tc_click_listener as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_plate)
            tc.addSemaphore(semaphore, To=False)

        with tc_main as tc:
            tc.addSemaphore(semaphore, From=True)
            tc.addFunction(self.movie_open.setLastFrame, False)
            tc.addFunction(self.movie_open_slot.addChild, self.en_movie_plate_content)
            tc.addPlay(self.movie_open, Wait=True)

            tc.addSemaphore(semaphore, From=False)
            tc.addFunction(self.movie_close.setLastFrame, False)
            tc.addFunction(self.movie_close_slot.addChild, self.en_movie_plate_content)
            tc.addPlay(self.movie_close, Wait=True)

    def cancelPlateEffectTC(self):
        for tc in self.__tcs:
            tc.cancel()

        self.__tcs = []


class CollectiblePlate(object):
    def __init__(self, collectibles_group, movie_state_block, movie_state_idle, movie_state_complete, movie_scene_icon,
                 movie_transition_text, movie_scene_icon_block, movie_text_transition_block):
        self.id = collectibles_group.collectible_group_id
        self.collectibles_group = collectibles_group
        self.states = {'Block': movie_state_block, 'Idle': movie_state_idle, 'Complete': movie_state_complete}
        self.movie_scene_icon = movie_scene_icon
        self.movie_text_transition = movie_transition_text

        self.movie_text_transition_block = movie_text_transition_block
        self.movie_scene_icon_block = movie_scene_icon_block
        self.current_state = None

        self.__tc_appear = None
        self.__tc_disappear = None
        self.__tc_play = None

        self.setCounterText()
        self.setCounterTextArgs()

    def setCounterText(self):
        self.movie_text_transition.setTextAliasEnvironment(str(self.id))
        Mengine.setTextAlias(str(self.id), ALIAS_COUNT, TEXT_ID_COUNT)

    def setCounterTextArgs(self):
        found_collectibles = self.collectibles_group.found_collectibles

        system_collectibles = SystemManager.getSystem('SystemCollectibles')
        collectibles_on_scene = system_collectibles.getCollectiblesOnScene(self.collectibles_group.params.scene_name)
        number_of_collectibles_on_scene = len(collectibles_on_scene) if collectibles_on_scene is not None else 0

        Mengine.setTextAliasArguments(str(self.id), ALIAS_COUNT, found_collectibles, number_of_collectibles_on_scene)

    def checkState(self, open_scenes):
        current_state = 'Block'

        if self.collectibles_group.complete:
            current_state = 'Complete'

        elif self.collectibles_group.scene_visited:
            current_state = 'Idle'

        return current_state

    def setState(self, state):
        movie_state = self.states.get(state, None)

        if movie_state is None:
            Trace.log('Manager', 0, 'CollectiblePlate does not have state {}'.format(state))
            return

        if self.current_state is not None:
            self.states.get(self.current_state).setEnable(False)

        movie_state.setEnable(True)
        self.current_state = state

    def collectibleTransitionIsOpen(self):
        if self.collectibles_group.complete:
            return False

        if self.collectibles_group.transition_padlock:
            return False

        if not self.collectibles_group.scene_visited:
            return False

        return True

    def runSocketEvents(self):
        if self.current_state is not 'Idle':
            return

        current_movie = self.states[self.current_state]
        movie_scene_icon_en = self.movie_scene_icon.getEntityNode()
        text_node = self.movie_text_transition.getEntityNode()

        if self.collectibles_group.transition_padlock:
            self.movie_scene_icon_block.setEnable(True)

            if self.movie_text_transition_block is not None:
                text_node = self.movie_text_transition_block.getEntityNode()

            self.__tc_play = TaskManager.createTaskChain(Name='{}_play_block_icon'.format(self.id), Repeat=True)
            with self.__tc_play as tc:
                tc.addTask('TaskMovie2SocketClick', Movie2=current_movie, SocketName='socket')
                tc.addPlay(self.movie_scene_icon_block, Wait=True)

        self.__tc_appear = TaskManager.createTaskChain(Name='{}_tc_appear'.format(self.id), Repeat=True)
        self.__tc_disappear = TaskManager.createTaskChain(Name='{}_tc_disappear'.format(self.id), Repeat=True)
        semaphore = Semaphore(False, '{}_semaphore'.format(self.id))

        with self.__tc_appear as tc:
            tc.addTask('TaskMovie2SocketEnter', Movie2=current_movie, SocketName='socket', isMouseEnter=False)
            tc.addSemaphore(semaphore, From=False)

            with tc.addRaceTask(2) as (enter, interrupt):
                with enter.addParallelTask(2) as (parallel_icon, parallel_text):
                    parallel_icon.addTask("TaskNodeAlphaTo", Node=movie_scene_icon_en, To=1.0, Time=FADE_TIME, Interrupt=True)
                    parallel_text.addTask("TaskNodeAlphaTo", Node=text_node, To=1.0, Time=FADE_TIME, Interrupt=True)

                interrupt.addTask('TaskMovie2SocketLeave', Movie2=current_movie, SocketName='socket', isMouseLeave=False)

            tc.addSemaphore(semaphore, To=True)

        with self.__tc_disappear as tc:
            tc.addTask('TaskMovie2SocketLeave', Movie2=current_movie, SocketName='socket', isMouseLeave=False)
            tc.addSemaphore(semaphore, From=True)

            with tc.addRaceTask(2) as (leave, interrupt):
                with leave.addParallelTask(2) as (parallel_icon, parallel_text):
                    parallel_icon.addTask("TaskNodeAlphaTo", Node=movie_scene_icon_en, To=0.0, Time=FADE_TIME, Interrupt=True)
                    parallel_text.addTask("TaskNodeAlphaTo", Node=text_node, To=0.0, Time=FADE_TIME, Interrupt=True)

                interrupt.addTask('TaskMovie2SocketEnter', Movie2=current_movie, SocketName='socket', isMouseEnter=False)

            tc.addSemaphore(semaphore, To=False)

    def cancelSocketEvents(self):
        if self.__tc_appear is not None:
            self.__tc_appear.cancel()
            self.__tc_appear = None

        if self.__tc_disappear is not None:
            self.__tc_disappear.cancel()
            self.__tc_disappear = None

        if self.__tc_play is not None:
            self.__tc_play.cancel()
            self.__tc_play = None

        if self.movie_scene_icon_block is not None:
            self.movie_scene_icon_block.entity.node.removeFromParent()
            self.movie_scene_icon_block.onFinalize()
            self.movie_scene_icon_block.onDestroy()
            self.movie_scene_icon_block = None

        if self.movie_text_transition_block is not None:
            self.movie_text_transition_block.entity.node.removeFromParent()
            self.movie_text_transition_block.onFinalize()
            self.movie_text_transition_block.onDestroy()
            self.movie_text_transition_block = None

        self.movie_text_transition.entity.node.removeFromParent()


class Collectibles(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("PreviousSceneName")
        Type.addActionActivate("CompleteScene")  # True if user collect all collectibles
        Type.addActionActivate("FinishAnimation")  # True if finish animation has been playing

        Type.addActionActivate('TransitionBackFromSceneName')
        Type.addActionActivate('TransitionBackToSceneName')
        Type.addActionActivate('TransitionBackToTextId')

    def __init__(self):
        super(Collectibles, self).__init__()
        self.collectible_movie_buttons = {}
        self.back_button = None
        self.tc_play_finish_animation = None
        self.tc_back_button = None
        self.onArrowActivateObserverID = None

        self.collectible_info_plate = None

    def _onPreparation(self):
        if self.object.hasObject('Movie2Button_Back'):
            self.back_button = self.object.getObject('Movie2Button_Back')

        self.__createPlates()

        self.movie_bg_idle = self.object.getObject('Movie2_BG_Idle')
        self.movie_bg_block = self.object.getObject('Movie2_BG_Block')
        self.movie_finish_animation = self.object.getObject('Movie2_FinishAnimation')

        self.movie_bg_idle.setEnable(self.CompleteScene)
        self.movie_bg_block.setEnable(not self.CompleteScene)
        self.movie_finish_animation.setEnable(self.CompleteScene)

        if self.FinishAnimation is True:
            self.movie_finish_animation.setEnable(False)

        if self.object.getParam("CompleteScene"):
            self.__disableCollectibleInfoPlate()
        else:
            self.__createCollectibleInfoPlate()

    def __createPlates(self):
        open_scenes = []
        if SystemManager.hasSystem("SystemMap2"):
            system_map = SystemManager.getSystem("SystemMap2")
            open_scenes = system_map.getAllMapsOpenScenes()

        scene_icon_block_prototype_name = None
        if self.object.hasPrototype('Movie2_SceneIconBlock'):
            scene_icon_block_prototype_name = 'Movie2_SceneIconBlock'

        text_block_prototype_name = None
        if self.object.hasPrototype('Movie2_TransitionTextBlock'):
            text_block_prototype_name = 'Movie2_TransitionTextBlock'

        arrow_node = Mengine.getArrowNode()

        system_collectibles = SystemManager.getSystem("SystemCollectibles")
        collectibles_groups = system_collectibles.getCollectibleGroups()

        for collectibles_group in collectibles_groups.values():
            plate = self.__createPlate(collectibles_group, arrow_node, scene_icon_block_prototype_name, text_block_prototype_name)

            if self.CompleteScene is False:
                current_state = plate.checkState(open_scenes)
                plate.setState(current_state)

            self.collectible_movie_buttons[collectibles_group.collectible_group_id] = plate

    def __createPlate(self, collectibles_group, arrow_node, scene_icon_block_prototype_name, text_block_prototype_name):
        movie_state_block = self.object.getObject(collectibles_group.params.icon_block_state_movie_name)
        movie_state_idle = self.object.getObject(collectibles_group.params.icon_idle_state_movie_name)
        movie_state_complete = self.object.getObject(collectibles_group.params.icon_complete_state_movie_name)
        movie_scene_icon = self.object.getObject(collectibles_group.params.scene_icon_name)
        movie_transition_text = self.object.getObject(collectibles_group.params.transition_text_movie_name)

        movie_scene_icon_block = None
        if scene_icon_block_prototype_name is not None:
            unique_name = '{}_scene_icon_block'.format(movie_scene_icon.getName())
            movie_scene_icon_block = self.object.generateObjectUnique(unique_name, scene_icon_block_prototype_name,
                                                                      Enable=True, Play=False, Loop=False)
            movie_scene_icon_block.setEnable(False)

            slot = movie_scene_icon.getMovieSlot('slot')
            if slot is not None:
                slot.addChild(movie_scene_icon_block.getEntityNode())

        movie_text_transition_block = None
        if text_block_prototype_name is not None:
            unique_name = '{}_text_block'.format(movie_scene_icon.getName())
            movie_text_transition_block = self.object.generateObjectUnique(unique_name, text_block_prototype_name,
                                                                           Enable=True, Play=False, Loop=False)
            movie_text_transition_block.setAlpha(0.0)
            arrow_node.addChild(movie_text_transition_block.getEntityNode())

        movie_state_block.setEnable(False)
        movie_state_idle.setEnable(False)
        movie_state_complete.setEnable(False)

        movie_scene_icon.setAlpha(0.0)
        movie_transition_text.setAlpha(0.0)

        arrow_node.addChild(movie_transition_text.getEntityNode())

        return CollectiblePlate(collectibles_group, movie_state_block, movie_state_idle, movie_state_complete,
                                movie_scene_icon, movie_transition_text, movie_scene_icon_block,
                                movie_text_transition_block)

    def __disableCollectibleInfoPlate(self):
        if self.object.hasObject('Movie2Button_Plate'):
            self.object.getObject('Movie2Button_Plate').setEnable(False)

        if self.object.hasObject('Movie2_PlateContent'):
            self.object.getObject('Movie2_PlateContent').setEnable(False)

        if self.object.hasObject('Movie2_Open'):
            self.object.getObject('Movie2_Open').setEnable(False)

        if self.object.hasObject('Movie2_Close'):
            self.object.getObject('Movie2_Close').setEnable(False)

    def __createCollectibleInfoPlate(self):
        if self.object.hasObject('Movie2Button_Plate'):
            button_plate = self.object.getObject('Movie2Button_Plate')
        else:
            return

        if self.object.hasObject('Movie2_PlateContent'):
            movie_plate_content = self.object.getObject('Movie2_PlateContent')
        else:
            return

        if self.object.hasObject('Movie2_Open'):
            movie_open = self.object.getObject('Movie2_Open')
        else:
            return

        if self.object.hasObject('Movie2_Close'):
            movie_close = self.object.getObject('Movie2_Close')
        else:
            return

        self.collectible_info_plate = CollectibleInfoPlate(button_plate, movie_plate_content, movie_open, movie_close)

    def _onActivate(self):
        if self.back_button is None:
            return

        self._runTaskChain()

    def _runTaskChain(self):
        if self.collectible_info_plate is not None:
            self.collectible_info_plate.runPlateEffectTC()

        def _runPlatesSocketEvents():
            for plate in self.collectible_movie_buttons.values():
                plate.runSocketEvents()
            return True

        # enable socket events after arrow activate, because TaskNodeAlphaTo can't work
        # with text_node that attached on disabled arrow (https://wonderland-games.atlassian.net/browse/CAME2-1313)
        self.onArrowActivateObserverID = Notification.addObserver(Notificator.onArrowActivate, _runPlatesSocketEvents)

        def _goPreviousScene():
            PreviousSceneName = self.PreviousSceneName or "Menu"
            TransitionManager.changeScene(PreviousSceneName)

        self.tc_back_button = TaskManager.createTaskChain()
        with self.tc_back_button as tc_back_button:  # click on cross for return on previous scene
            tc_back_button.addTask('TaskMovie2ButtonClick', Movie2Button=self.back_button)
            tc_back_button.addFunction(_goPreviousScene)
            tc_back_button.addFunction(self.object.setParam, "PreviousSceneName", None)

        self.tc_transition_on_scenes = TaskManager.createTaskChain()
        with self.tc_transition_on_scenes as tc_transition_on_scenes:  # transition on scene for complete collectibles
            for (plate, tc_plate) in tc_transition_on_scenes.addRaceTaskList(self.collectible_movie_buttons.values()):
                with tc_plate.addIfTask(plate.collectibleTransitionIsOpen) as (true, false):
                    true.addTask('TaskMovie2SocketClick', Movie2=plate.states.get('Idle'), SocketName='socket')
                    true.addFunction(self.__setSpecialCollectibleTransition, plate.collectibles_group.params.scene_name)
                    true.addFunction(TransitionManager.changeScene, plate.collectibles_group.params.scene_name)

                    false.addBlock()

        if self.CompleteScene is False or self.FinishAnimation is True:
            return

        self.tc_play_finish_animation = TaskManager.createTaskChain()
        with self.tc_play_finish_animation as tc_play_finish_animation:  # finish animation
            with GuardBlockInput(tc_play_finish_animation) as guard_tc_play_finish_animation:
                guard_tc_play_finish_animation.addPlay(self.movie_finish_animation)
                guard_tc_play_finish_animation.addDisable(self.movie_finish_animation)
                guard_tc_play_finish_animation.addFunction(self.object.setParam, 'FinishAnimation', True)

    def __setSpecialCollectibleTransition(self, scene_name_from):
        system_collectibles = SystemManager.getSystem('SystemCollectibles')
        prev_scene = self.object.getParam('PreviousSceneName')
        system_collectibles.setCollectibleTransition(scene_name_from, prev_scene)

    def _onDeactivate(self):
        self.__cleanUp()

    def __cleanUp(self):
        for plate in self.collectible_movie_buttons.values():
            plate.cancelSocketEvents()

        if self.onArrowActivateObserverID is not None:
            Notification.removeObserver(self.onArrowActivateObserverID)
            self.onArrowActivateObserverID = None

        self.collectible_movie_buttons = {}

        if self.collectible_info_plate is not None:
            self.collectible_info_plate.cancelPlateEffectTC()

        if self.tc_back_button is not None:
            self.tc_back_button.cancel()
            self.tc_back_button = None

        if self.tc_play_finish_animation is not None:
            self.tc_play_finish_animation.cancel()
            self.tc_play_finish_animation = None

        if self.tc_transition_on_scenes is not None:
            self.tc_transition_on_scenes.cancel()
            self.tc_transition_on_scenes = None
