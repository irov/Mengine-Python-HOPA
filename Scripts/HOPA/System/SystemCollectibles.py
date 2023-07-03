from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import isCollectorEdition
from HOPA.CollectiblesManager import CollectiblesManager
from HOPA.HintManager import HintManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification


QUEST_TYPE = 'CollectibleItem'
HINT_ACTION_TYPE = 'HintActionCollectibleItem'

PUZZLE_INVENTORY_NAME = 'PuzzleInventory'
TEXT_ID_PUZZLE_INV = 'ID_COLLECTIBLES_TRANSITION_PUZZLE_INV_TEXT'
ID_EMPTY_TEXT = "ID_EMPTY_TEXT"

COLLECTIBLES_SCENE_NAME = 'Collectibles'
BONUS_SCENE_NAME = 'Bonus'

TEXT_ID_TRANSITION_BACK = 'ID_TransitionCollectibles'


class CollectibleGroup(object):
    def __init__(self, params):
        self.collectible_group_id = params.collectible_group_id
        self.params = params
        self.complete = False
        self.has_progress = False
        self.found_collectibles = 0

        # if scene has macro padlock, then collectibles scene transition will be blocked until macro command run
        self.transition_padlock = False

        # if this is true, and !complete allow special collectible transition to CollectibleGroup scene
        self.scene_visited = False

    def setProgress(self):
        self.has_progress = True

    def hasProgress(self):
        return self.has_progress

    def setComplete(self, value):
        self.complete = value

    def isComplete(self):
        return self.complete

    def setTransitionPadlock(self, transition_padlock):
        self.transition_padlock = transition_padlock


class Collectible(object):
    def __init__(self, params):
        self.collectible_id = params.item_id
        self.params = params
        self.complete = False

    def setComplete(self, value):
        self.complete = value

    def isComplete(self):
        return self.complete


class SystemCollectibles(System):
    s_dev_to_debug = False
    s_search_mode = False

    s_collectibles_groups = {}
    s_collectibles = {}
    s_collectibles_by_scenes = {}

    def _onParams(self, _params):
        self.tc = None
        self.keyHandlerId = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

    def __checkCE(self):
        return isCollectorEdition()

    def _onRun(self):
        if self.__checkCE() is False:
            self.disableCollectibles()
            return True

        SystemCollectibles.s_collectibles_groups = {}
        SystemCollectibles.s_collectibles = {}
        SystemCollectibles.s_collectibles_by_scenes = {}

        collectibles_params = CollectiblesManager.getCollectibleParams()
        collectible_groups_params = CollectiblesManager.getCollectiblesSceneParams()

        self.__createCollectible(collectibles_params)
        self.__createCollectibleGroups(collectible_groups_params)

        self.__setObservers()

        self.__addDevToDebug()
        return True

    def disableCollectibles(self):
        collectibles_params = CollectiblesManager.getCollectibleParams()
        for param in collectibles_params.values():
            group = GroupManager.getGroup(param.group_name)
            if isinstance(group, GroupManager.EmptyGroup) is True:
                continue
            movies = [param.movie_collect, param.movie_collect_idle_state]
            for movie_name in movies:
                if group.hasObject(movie_name) is False:
                    continue

                movie = group.getObject(movie_name)
                movie.setEnable(False)

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemCollectibles.s_dev_to_debug is True:
            return
        SystemCollectibles.s_dev_to_debug = True

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        w_scene = Mengine.createDevToDebugWidgetButton("collectibles_complete_scene")
        w_scene.setTitle("Get all scene collectibles")
        w_scene.setClickEvent(SystemCollectibles.completeCurrentSceneCollectibles)
        tab.addWidget(w_scene)

        def _onSceneInit(scene_name):
            if SystemCollectibles.__checkCompleteCollectibles(scene_name) is False:
                w_scene.setHide(True)
                return True

            w_scene.setHide(False)
            return False

        self.addObserver(Notificator.onSceneInit, _onSceneInit)

    def __setObservers(self):
        self.addObserver(Notificator.onCollectiblesPart, self.__cbCollectiblesPart)
        self.addObserver(Notificator.onTransitionEnd, self.__cbTransitionEnd)

        self.addObserver(Notificator.onSceneEnter, self.__cbSceneEnter)

    def __cbSceneEnter(self, scene_name):
        """Update scene_visited param for CollectibleGroup instance
        """

        if scene_name in SystemCollectibles.s_collectibles_groups:
            if CollectiblesManager.isSceneInBlockVisited(scene_name) is True:
                return False

            SystemCollectibles.s_collectibles_groups[scene_name].scene_visited = True

        return False

    @staticmethod
    def isSearchMode():
        return SystemCollectibles.s_search_mode is True

    def setCollectibleTransition(self, scene_name, scene_before_collectibles_scene):
        # Set Transition Back
        transition_back_to_scene_name = TransitionManager.getTransitionBack(scene_name)
        transition_back_to_text_id = TransitionManager.getTransitionBackShow(scene_name)

        TransitionManager.setTransitionBack(scene_name, COLLECTIBLES_SCENE_NAME)
        TransitionManager.setTransitionBackShow(scene_name, TEXT_ID_TRANSITION_BACK)

        SystemCollectibles.s_search_mode = True

        # restart search mode if we do scene restart
        self.addObserver(Notificator.onSceneRestartBegin, self.__cbSceneRestartBegin, scene_name, scene_before_collectibles_scene)

        self.addObserver(Notificator.onSceneDeactivate, self.__cbCollectibleTransitionEnd, scene_name)
        self.addObserver(Notificator.onSceneInit, self.__cbCollectibleTransition, transition_back_to_scene_name, transition_back_to_text_id, scene_before_collectibles_scene)

    def __cbSceneRestartBegin(self, scene_name, scene_before_collectibles_scene):
        if SystemCollectibles.s_search_mode is False:
            return True

        def _cb(deactivate_scene_name):
            # todo: self.setCollectibleTransition(scene_name, scene_before_collectibles_scene)
            TransitionManager.changeScene(COLLECTIBLES_SCENE_NAME)
            return True

        self.addObserver(Notificator.onSceneDeactivate, _cb)
        return True

    @staticmethod
    def __cbCollectibleTransitionEnd(scene_name, search_scene_name):
        if scene_name == search_scene_name:
            SystemCollectibles.s_search_mode = False
            return True
        return False

    @staticmethod
    def __cbCollectibleTransition(scene_name, transition_back_to_scene_name,
                                  transition_back_to_text_id, scene_before_collectibles_scene):
        group_name = SceneManager.getSceneMainGroupName(scene_name)

        """
        disable Groups
        """
        disabled_group_main_layer_en = []
        group_to_disable_names = CollectiblesManager.getCollectiblesGroupToDisableNames()

        for group_name_ in group_to_disable_names:
            if not GroupManager.hasGroup(group_name_):
                continue
            group = GroupManager.getGroup(group_name_)
            entity_node = group.getMainLayer()

            if not entity_node.isEnable():
                continue

            entity_node.disable()
            disabled_group_main_layer_en.append(entity_node)

        """
        Swap Inventory
        """
        puzzle_inv_demon = None
        cur_inv_group = None
        puzzle_inv_group = None

        if SystemManager.hasSystem('SystemInventoryPanel'):
            system_inventory_panel = SystemManager.getSystem('SystemInventoryPanel')
            cur_inv_name = system_inventory_panel.getActiveInventoryName()

            if DemonManager.hasDemon(PUZZLE_INVENTORY_NAME):
                puzzle_inv_demon = DemonManager.getDemon(PUZZLE_INVENTORY_NAME)
                puzzle_inv_demon.setTextID(TEXT_ID_PUZZLE_INV)

                cur_inv_group = SceneManager.getSceneLayerGroup(scene_name, cur_inv_name)
                cur_inv_group.onDisable()

                puzzle_inv_group = SceneManager.getSceneLayerGroup(scene_name, PUZZLE_INVENTORY_NAME)
                puzzle_inv_group.onEnable()

        """
        block gui buttons
        """
        button_block_params = CollectiblesManager.getCollectiblesButtonBlockParams()
        for (group_name_, button_block_param) in button_block_params.items():
            button_block_param.blockButtons(GroupManager)

        """
        enable "collectibles_block_socket"
        """
        group = GroupManager.getGroup(group_name)
        saved_group_layer_order = list(group.layers_order)  # save scene group order before transition
        size = group.main_layer.size
        main_layer_node = group.getMainLayer()

        socket_block = Mengine.createNode("HotSpotPolygon")
        socket_block.setName(str('collectibles_block_socket'))
        socket_block.setPolygon([(size[0], 0), size, (0, size[1]), (0, 0)])
        main_layer_node.addChild(socket_block)

        collectibles = SystemCollectibles.getCollectiblesOnScene(scene_name)
        for collectible in collectibles:
            if collectible.isComplete():
                continue

            """
            collectibles movie to top level
            """
            movie_idle = collectible.params.movie_collect_idle_state
            movie_collect = collectible.params.movie_collect
            if GroupManager.hasObject(group_name, movie_idle):
                collectible_movie = GroupManager.getObject(group_name, movie_idle)
            else:
                collectible_movie = GroupManager.getObject(group_name, movie_collect)

            en_collectible_movie = collectible_movie.getEntityNode()

            main_layer_node.addChild(en_collectible_movie)

            """
            collectibles movie hint action
            """
            if QUEST_TYPE not in QuestManager.s_questsTypes:
                continue

            if HINT_ACTION_TYPE not in HintManager.s_actions:
                continue

            tc = TaskManager.createTaskChain()
            quest = QuestManager.createLocalQuest(QUEST_TYPE, SceneName=scene_name, GroupName=group_name,
                                                  Object=collectible_movie)
            HintManager.createHintAction(HINT_ACTION_TYPE, quest, SceneName=scene_name, GroupName=group_name,
                                         Object=collectible_movie)

            with tc as tc:
                with QuestManager.runQuest(tc, quest) as tc_quest:
                    with tc_quest.addRaceTask(2) as (race_1, race_2):
                        race_1.addTask("TaskMovie2SocketClick", Group=group, Movie2=collectible_movie, SocketName="socket")
                        race_2.addListener(Notificator.onSceneDeactivate)

        """
        Collectible Transition Finish revert actions
        """
        with TaskManager.createTaskChain() as tc:
            with tc.addRaceTask(2) as (race_1, race_2):
                race_1.addListener(Notificator.onSceneDeactivate)  # when player activate transition
                race_2.addListener(Notificator.onCollectiblesPart,  # force transition when all collectibles founded:
                                   Filter=lambda scene_name_, *_: SystemCollectibles.__checkCompleteCollectibles(scene_name_))
                race_2.addFunction(TransitionManager.changeScene, COLLECTIBLES_SCENE_NAME)
                race_2.addListener(Notificator.onSceneDeactivate)

            # for case when close_game/menu_exit, this is for session save/load
            if scene_before_collectibles_scene is not BONUS_SCENE_NAME:
                tc.addFunction(SceneManager.setCurrentGameSceneName, scene_before_collectibles_scene)

            """
            revert disabled groups
            """
            for entity_node in disabled_group_main_layer_en:
                tc.addFunction(entity_node.enable)

            """
            Reset Puzzle Inv Text
            """

            def groupSetEnable(group_, enable):
                group_.enable = enable

            if puzzle_inv_demon is not None:
                tc.addFunction(puzzle_inv_demon.setTextID, ID_EMPTY_TEXT)
                tc.addFunction(groupSetEnable, puzzle_inv_group, False)
                tc.addFunction(groupSetEnable, cur_inv_group, True)

            """
            disable "collectibles_block_socket"
            """
            tc.addFunction(socket_block.removeFromParent)
            tc.addFunction(Mengine.destroyNode, socket_block)

            """
            collectibles movie restore order
            """

            def resetGroupLayerOrder():
                group.layers_order = saved_group_layer_order

            tc.addFunction(resetGroupLayerOrder)

            """
            revert block gui buttons
            """
            for (group_name_, button_block_param) in button_block_params.items():
                tc.addFunction(button_block_param.revertButtonBlock)

            """
            restore Transition Back
            """
            if transition_back_to_scene_name is None:
                tc.addFunction(TransitionManager.popTransitionBack, scene_name)
            else:
                tc.addFunction(TransitionManager.setTransitionBack, scene_name, transition_back_to_scene_name)

            if transition_back_to_text_id is None:
                tc.addFunction(TransitionManager.popTransitionBackShow, scene_name)
            else:
                tc.addFunction(TransitionManager.setTransitionBackShow, scene_name, transition_back_to_text_id)

        return True

    @staticmethod
    def __createCollectible(collectibles_params):
        for params in collectibles_params.values():
            collectible = Collectible(params)
            SystemCollectibles.s_collectibles[params.item_id] = collectible
            SystemCollectibles.__addCollectiblesByScene(collectible, collectible.params.scene)

    @staticmethod
    def __addCollectiblesByScene(param, scene_name):
        params_on_scene = SystemCollectibles.s_collectibles_by_scenes.get(scene_name, None)

        if params_on_scene is None:
            params_on_scene = []

        params_on_scene.append(param)
        SystemCollectibles.s_collectibles_by_scenes[scene_name] = params_on_scene

    @staticmethod
    def __createCollectibleGroups(collectible_groups_params):
        for param in collectible_groups_params.values():
            collectibles_group = CollectibleGroup(param)
            SystemCollectibles.s_collectibles_groups[param.scene_name] = collectibles_group

    @staticmethod
    def getCollectibles():
        return SystemCollectibles.s_collectibles

    @staticmethod
    def getCollectibleGroups():
        return SystemCollectibles.s_collectibles_groups

    @staticmethod
    def getCollectibleGroup(collectible_group_name):
        return SystemCollectibles.s_collectibles_groups.get(collectible_group_name)

    @staticmethod
    def getCollectiblesOnScene(scene_name):
        return SystemCollectibles.s_collectibles_by_scenes.get(scene_name)

    @staticmethod
    def completeAllCollectibles():  # cheat
        if SystemCollectibles.__checkCompleteAllCollectibles() is True:
            return

        current_scene = SceneManager.getCurrentSceneName()

        collectibles_scene_params = SystemCollectibles.getCollectibleGroups()
        for scene_name, collectibles_scene_group in collectibles_scene_params.items():
            if collectibles_scene_group.isComplete() is True:
                continue

            collectibles_on_scene = SystemCollectibles.getCollectiblesOnScene(scene_name)
            for collectible in collectibles_on_scene:
                if current_scene == scene_name:
                    SystemCollectibles.__fastSceneCollect(collectible)
                else:
                    collectible.setComplete(True)
                collectibles_scene_group.found_collectibles += 1

            collectibles_scene_group.setComplete(True)

        Notification.notify(Notificator.onAddAchievementPlateToQueue, 'Collectibles', current_scene)
        return SystemCollectibles.__checkCompleteAllCollectibles()

    @staticmethod
    def __fastSceneCollect(collectible):  # cheat util
        group_name = collectible.params.group_name
        movie_idle_name = collectible.params.movie_collect_idle_state

        movie_collect = GroupManager.getObject(group_name, collectible.params.movie_collect)
        movie_idle = None
        if GroupManager.hasObject(group_name, movie_idle_name):
            movie_idle = GroupManager.getObject(group_name, movie_idle_name)

        with TaskManager.createTaskChain(Name="FastCollectibleCollect_{}".format(collectible.collectible_id)) as tc:
            if movie_idle is not None:
                movie_idle.setPlay(False)
                movie_idle.setEnable(False)

            tc.addEnable(movie_collect)
            tc.addPlay(movie_collect, Wait=True, Loop=False)
            tc.addDisable(movie_collect)

        collectible.setComplete(True)

    @staticmethod
    def completeCurrentSceneCollectibles():  # cheat
        scene_name = SceneManager.getCurrentSceneName()
        collectibles = SystemCollectibles.getCollectiblesOnScene(scene_name)
        if collectibles is None:
            return

        complete_collectibles = SystemCollectibles.__checkCompleteCollectibles(scene_name)
        if complete_collectibles is True:
            return

        for collectible in collectibles:
            SystemCollectibles.__fastSceneCollect(collectible)
        Notification.notify(Notificator.onCollectiblesPart, scene_name, len(collectibles))

        collectible_scene_group = SystemCollectibles.getCollectibleGroup(scene_name)
        collectible_scene_group.setComplete(True)

        if Mengine.isAvailablePlugin("DevToDebug") is True:
            tab = Mengine.getDevToDebugTab("Cheats")
            widget = tab.findWidget("collectibles_complete_scene")
            widget.setHide(True)

    @staticmethod
    def __onGlobalHandleKeyEvent(event):
        if Mengine.hasOption("cheats") is False:
            return
        if event.isDown is False:
            return

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return

        if event.code == DefaultManager.getDefaultKey("CheatsCompleteSceneCollectibles"):
            SystemCollectibles.completeCurrentSceneCollectibles()
        elif event.code == DefaultManager.getDefaultKey("CheatsCompleteAllCollectibles"):
            SystemCollectibles.completeAllCollectibles()

    def __cbTransitionEnd(self, _scene_from, scene_to, _zoom_group_name):
        collectibles = SystemCollectibles.s_collectibles_by_scenes.get(scene_to)
        if collectibles is None:
            return False

        collectible_group = SystemCollectibles.getCollectibleGroup(scene_to)

        if collectible_group is None:
            return False

        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.__runTaskChain(collectibles, scene_to)
        return False

    def __runTaskChain(self, collectibles, scene_name):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            for collectible, race_source in tc.addParallelTaskList(collectibles):
                with race_source.addIfTask(collectible.isComplete) as (true, false):
                    group_name = collectible.params.group_name
                    idle_state = collectible.params.movie_collect_idle_state

                    if GroupManager.hasObject(group_name, idle_state):
                        movie_idle = GroupManager.getObject(group_name, idle_state)
                        true.addDisable(movie_idle)

                    movie_collect = GroupManager.getObject(group_name, collectible.params.movie_collect)
                    true.addDisable(movie_collect)

                    true.addBlock()

                    false.addScope(self.__sourceTaskClick, collectible)
                    false.addNotify(Notificator.onCollectiblesPart, scene_name)
                    false.addFunction(self.__checkCompleteCollectibles, scene_name)

    @staticmethod
    def __sourceTaskClick(source, collectible):
        """ In this method waiting click on collectible item, playing collect animation, and complete collectible item

        :param source:
        :param collectible:
                    if movie_collect_idle_state is None instead of him setup movie_collect in first frame and waiting
                    click on this movie.
                    if movie_collect_idle_state is not None, playing in loop movie_collect_idle_state and waiting click
                    on this movie
        :return:
        """

        movie_idle = None
        if GroupManager.hasObject(collectible.params.group_name, collectible.params.movie_collect_idle_state):
            movie_idle = GroupManager.getObject(collectible.params.group_name,
                                                collectible.params.movie_collect_idle_state)

        movie_collect = GroupManager.getObject(collectible.params.group_name, collectible.params.movie_collect)

        with source.addRaceTask(2) as (source_click, source_idle_play):
            if movie_idle is None:
                source_click.addEnable(movie_collect)
                source_click.addTask("TaskMovie2SocketClick", SocketName="socket", Movie2=movie_collect)

            else:
                source_click.addDisable(movie_collect)
                source_click.addTask("TaskMovie2SocketClick", SocketName="socket", Movie2=movie_idle)
                source_click.addTask('TaskMovie2Stop', Movie2=movie_idle)
                source_click.addDisable(movie_idle)
                source_click.addEnable(movie_collect)

                source_idle_play.addPlay(movie_idle, Loop=True)

            source_idle_play.addBlock()

        with GuardBlockInput(source) as guard_source:
            guard_source.addPlay(movie_collect, Loop=False)
            guard_source.addDisable(movie_collect)
            guard_source.addFunction(collectible.setComplete, True)

    def __cbCollectiblesPart(self, scene_name, count=1):
        self.__checkCompleteCollectibles(scene_name)

        collectibles_scene_param = SystemCollectibles.getCollectibleGroup(scene_name)
        collectibles_scene_param.found_collectibles += count

        Notification.notify(Notificator.onAddAchievementPlateToQueue, 'Collectibles', scene_name)

        return self.__checkCompleteAllCollectibles()

    @staticmethod
    def __checkCompleteAllCollectibles():
        """ This method check have we found all items in the game

        :return: True if we have found all items in the game, else False
        """

        collectibles_scene_params = SystemCollectibles.getCollectibleGroups()
        for collectible_scene_param in collectibles_scene_params.values():
            if not collectible_scene_param.isComplete():
                return False

        demon_collectibles = DemonManager.getDemon('Collectibles')
        demon_collectibles.setParam('CompleteScene', True)
        Notification.notify(Notificator.onCollectiblesComplete)
        return True

    @staticmethod
    def __checkCompleteCollectibles(scene_name):
        """ This method check have we found all the items available in this scene

        :param scene_name: scene name which is being verified
        :return: True if all collectibles on scene is found else False
        """

        collectibles_params = SystemCollectibles.getCollectiblesOnScene(scene_name)
        if collectibles_params is None:
            return False

        is_progress = False
        is_complete = True
        for collectibles_on_scene_param in collectibles_params:
            if collectibles_on_scene_param.isComplete():
                is_progress = True
                continue
            is_complete = False

        collectible_scene_pram = SystemCollectibles.getCollectibleGroup(scene_name)
        if is_progress is True:
            collectible_scene_pram.setProgress()
        if is_complete is True:
            collectible_scene_pram.setComplete(True)

        return is_complete

    @classmethod
    def _onSave(cls):
        save_collectibles = {
            'Collectibles': [],
            'CollectibleGroups': {
                'Completed': [],
                'Progress': [],
                'FoundCollectibles': {},
                'SceneVisited': []
            }
        }

        collectibles_data = save_collectibles['Collectibles']
        for collectible in cls.getCollectibles().values():
            if collectible.isComplete():
                collectibles_data.append(collectible.collectible_id)

        collectible_groups_data_completed = save_collectibles['CollectibleGroups']['Completed']
        collectible_groups_data_progress = save_collectibles['CollectibleGroups']['Progress']
        collectible_groups_data_found_collectibles = save_collectibles['CollectibleGroups']['FoundCollectibles']
        collectible_groups_data_scene_visited = save_collectibles['CollectibleGroups']['SceneVisited']

        for scene_name, collectible_scene_param in cls.getCollectibleGroups().iteritems():
            if collectible_scene_param.complete is True:
                collectible_groups_data_completed.append(scene_name)

            if collectible_scene_param.has_progress is True:
                collectible_groups_data_progress.append(scene_name)

            found_collectibles = collectible_scene_param.found_collectibles
            if found_collectibles > 0:
                collectible_groups_data_found_collectibles[scene_name] = found_collectibles

            if collectible_scene_param.scene_visited is True:
                collectible_groups_data_scene_visited.append(scene_name)

        return save_collectibles

    @classmethod
    def _onLoad(cls, save_collectibles):
        # CHECK

        if not isinstance(save_collectibles, dict):
            return

        collectibles_data = save_collectibles.get('Collectibles')
        if collectibles_data is None:
            return

        collectibles_groups_data = save_collectibles.get('CollectibleGroups')
        if collectibles_groups_data is None:
            return

        # LOAD

        for item_id, collectible_param in cls.getCollectibles().iteritems():
            if item_id in collectibles_data:
                collectible_param.setComplete(True)

        collectible_groups_data_completed = collectibles_groups_data.get('Completed', [])
        collectible_groups_data_progress = collectibles_groups_data.get('Progress', [])
        collectible_groups_data_found_collectibles = collectibles_groups_data.get('FoundCollectibles', {})
        collectible_groups_data_scene_visited = collectibles_groups_data.get('SceneVisited', [])

        for scene_name, collectible_scene_param in cls.getCollectibleGroups().iteritems():
            if scene_name in collectible_groups_data_completed:
                collectible_scene_param.setComplete(True)

            if scene_name in collectible_groups_data_progress:
                collectible_scene_param.setProgress()

            if scene_name in collectible_groups_data_progress:
                collectible_scene_param.found_collectibles = collectible_groups_data_found_collectibles.get(scene_name, 0)

            if scene_name in collectible_groups_data_scene_visited:
                collectible_scene_param.scene_visited = True

    def _onStop(self):
        super(SystemCollectibles, self)._onStop()
        Mengine.removeGlobalHandler(self.keyHandlerId)
