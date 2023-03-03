from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager


class CollectiblesManager(Manager):
    s_collectibles_params = {}
    s_collectibles_scene_params = {}
    s_collectibles_button_block_params = {}
    s_collectibles_group_to_disable_names = []
    s_collectibles_block_visited_params = {}

    class CollectibleParam(object):
        def __init__(self, item_id, scene_name, movie_collect_name, movie_collect_idle_state_name, group_name):
            self.item_id = item_id
            self.scene = scene_name
            self.movie_collect = movie_collect_name
            self.movie_collect_idle_state = movie_collect_idle_state_name
            self.group_name = group_name

    class CollectibleSceneParam(object):
        def __init__(self, collectible_group_id, scene_name, transition_text_movie_name, icon_block_state_movie_name,
                     icon_idle_state_movie_name, icon_complete_state_movie_name, scene_icon_name):
            self.collectible_group_id = collectible_group_id
            self.scene_name = scene_name
            self.transition_text_movie_name = transition_text_movie_name
            self.icon_block_state_movie_name = icon_block_state_movie_name
            self.icon_idle_state_movie_name = icon_idle_state_movie_name
            self.icon_complete_state_movie_name = icon_complete_state_movie_name
            self.scene_icon_name = scene_icon_name

    class CollectibleButtonBlockParam(object):
        def __init__(self, group_name, button_whitelist_names):
            self.group_name = group_name
            self.button_whitelist_names = button_whitelist_names
            self.blocked_button_objects_buffer = []

        def visitor(self, obj_):
            obj_type = obj_.getType()
            if obj_type == 'ObjectMovie2Button' or obj_type == 'ObjectMovieButton':
                if obj_.getBlock():
                    return
                if obj_.getName() in self.button_whitelist_names:
                    return

                obj_.setBlock(True)
                self.blocked_button_objects_buffer.append(obj_)

        def blockButtons(self, group_manager):
            if group_manager.hasGroup(self.group_name) is False:
                return

            group = group_manager.getGroup(self.group_name)
            if isinstance(group, GroupManager.EmptyGroup) is True:
                return

            group.visitObjects2(self.visitor)

        def revertButtonBlock(self):
            for button in self.blocked_button_objects_buffer:
                button.setBlock(False)
            self.blocked_button_objects_buffer = []

    class CollectiblesVisitedBlock(object):
        def __init__(self, scene_name, block_visited):
            self.scene_name = scene_name
            self.block_visited = block_visited

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            """
            Collectibles.xlsx:
            ItemID	SceneName	MovieCollectName	MovieCollectIdleStateName	GroupName
            
            CollectiblesScene.xlsx:
            CollectibleGroupID	SceneName	IconBlockState	IconIdleState	IconCompleteState
            
            CollectiblesTransitionButtonBlock.xlsx:
            ButtonBlockGroupName	[ButtonBlockButtonNameWhiteList]
            
            CollectiblesTransitionGroupDisable.xlsx
            GroupNameToDisable
            """

            item_id = record.get("ItemID")
            collectible_group_id = record.get("CollectibleGroupID")
            button_block_group_name = record.get("ButtonBlockGroupName")
            group_name_to_disable = record.get("GroupNameToDisable")
            block_visited = record.get("BlockAutoSceneVisited")

            if item_id is not None:
                CollectiblesManager.__loadCollectiblesParam(record)
            elif block_visited is not None:
                CollectiblesManager.__loadCollectiblesVisitedBlock(record)
            elif collectible_group_id is not None:
                CollectiblesManager.__loadCollectiblesSceneParam(record)
            elif button_block_group_name is not None:
                CollectiblesManager.__loadCollectiblesTransitionButtonBlockParam(record)
            elif group_name_to_disable is not None:
                CollectiblesManager.s_collectibles_group_to_disable_names.append(group_name_to_disable)
        return True

    @staticmethod
    def __loadCollectiblesTransitionButtonBlockParam(record):
        """
        :param record: ButtonBlockGroupName	[ButtonBlockButtonNameWhiteList]
        :return:
        """
        group_name = record.get("ButtonBlockGroupName")
        button_whitelist_names = record.get("ButtonBlockButtonNameWhiteList", [])

        button_block_param = CollectiblesManager.CollectibleButtonBlockParam(group_name, button_whitelist_names)

        CollectiblesManager.s_collectibles_button_block_params[group_name] = button_block_param

    @staticmethod
    def __loadCollectiblesParam(record):
        """
            :param record: ItemID	SceneName	MovieCollectName	MovieCollectIdleState	GroupName
            :return:
        """
        item_id = record.get("ItemID")
        scene_name = record.get("SceneName")
        movie_collect_name = record.get("MovieCollectName")
        movie_collect_idle_state_name = record.get("MovieCollectIdleStateName")
        group_name = record.get("GroupName")

        collectibles_param = CollectiblesManager.CollectibleParam(item_id, scene_name, movie_collect_name,
                                                                  movie_collect_idle_state_name, group_name)

        CollectiblesManager.s_collectibles_params[item_id] = collectibles_param

    @staticmethod
    def __loadCollectiblesSceneParam(record):
        """
        :param record: CollectibleGroupID	SceneName	TransitionText	SceneIcon	CompleteState	IdleState	BlockState
        :return:
        """
        collectible_group_id = record.get("CollectibleGroupID")
        scene_name = record.get("SceneName")
        icon_block_state_movie_name = record.get("BlockState")
        icon_idle_state_movie_name = record.get("IdleState")
        icon_complete_state_movie_name = record.get("CompleteState")
        transition_text_movie_name = record.get("TransitionText")
        scene_icon_name = record.get("SceneIcon")
        collectible_scene_param = CollectiblesManager.CollectibleSceneParam(collectible_group_id, scene_name,
                                                                            transition_text_movie_name,
                                                                            icon_block_state_movie_name,
                                                                            icon_idle_state_movie_name,
                                                                            icon_complete_state_movie_name,
                                                                            scene_icon_name)
        CollectiblesManager.s_collectibles_scene_params[scene_name] = collectible_scene_param

    @staticmethod
    def __loadCollectiblesVisitedBlock(record):
        scene_name = record["SceneName"]
        block_visited = record.get("BlockAutoSceneVisited", True)

        block_visited_param = CollectiblesManager.CollectiblesVisitedBlock(scene_name, block_visited)

        CollectiblesManager.s_collectibles_block_visited_params[scene_name] = block_visited_param

    @staticmethod
    def getCollectibleParams():
        return CollectiblesManager.s_collectibles_params

    @staticmethod
    def getCollectiblesSceneParam(scene_name):
        return CollectiblesManager.s_collectibles_scene_params.get(scene_name, None)

    @staticmethod
    def getCollectiblesSceneParams():
        return CollectiblesManager.s_collectibles_scene_params

    @staticmethod
    def getCollectiblesButtonBlockParams():
        return CollectiblesManager.s_collectibles_button_block_params

    @staticmethod
    def getCollectiblesGroupToDisableNames():
        return CollectiblesManager.s_collectibles_group_to_disable_names

    @staticmethod
    def getCollectiblesBlockVisitedParams():
        return CollectiblesManager.s_collectibles_block_visited_params

    @staticmethod
    def isSceneInBlockVisited(scene_name):
        param = CollectiblesManager.s_collectibles_block_visited_params.get(scene_name, None)
        if param is None:
            return False
        return param.block_visited
