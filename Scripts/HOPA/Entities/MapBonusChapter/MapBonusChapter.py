from Event import Event
from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification

EVENT_SHOW_OVERVIEW = Event("onShowOverview")
EVENT_HIDE_OVERVIEW = Event("onHideOverview")

class MapBonusChapter(BaseEntity):
    quest_check_types = ["UseInventoryItem", "GiveItemOr", "CompleteItemCount"]
    quests_all_done = False

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "OpenScenes", Append=MapBonusChapter.__appendOpenScenes, Update=MapBonusChapter.__updateOpenScenes)
        Type.addActionActivate(Type, "BlockedScenes")
        Type.addActionActivate(Type, "OpenHog")
        Type.addActionActivate(Type, "PlayedOpenHog")
        Type.addActionActivate(Type, "CompletedScenes")

    def __appendOpenScenes(self, index, scene_name):
        Map2Manager.s_open_scenes.append(scene_name)

    def __updateOpenScenes(self, value):
        Map2Manager.s_open_scenes = value

    def __init__(self):
        super(MapBonusChapter, self).__init__()
        Notification.notify(Notificator.onMapEntityInit)
        self.movie_objects = []
        self.sockets = {}
        self.hog_collection = {}
        self.all_done_scenes = []
        self.zoom_effect_zoom_factor = DefaultManager.getDefaultFloat("TransitionZoomEffectFactor", 1.5)
        self.time_zoom_in = DefaultManager.getDefaultFloat("TransitionFadeOutTime", 0.1) * 1000  # speed fix

    def generateMovie(self, prototype_name, slot_id, slot):
        movie = self.object.generateObject(prototype_name + slot_id, prototype_name)
        self.movie_objects.append(movie)
        movie.setEnable(True)
        movie_entity = movie.getEntityNode()
        slot.addChild(movie_entity)
        return movie

    def getCurrentLocation(self):
        object_name = self.object.getName()
        map_data = Map2Manager.getMapData(object_name)
        locations = map_data.getLocations()

        check_scene_name = SceneManager.getCurrentGameSceneName()
        for loc, scenes in locations.iteritems():
            if loc not in self.OpenScenes:
                continue

            for scene_name, group_name, main in scenes:
                if check_scene_name == scene_name:
                    return loc

        collection = map_data.getCollection()
        for keys in collection:
            for minigame in collection[keys].getMinigames():
                if minigame == check_scene_name:
                    return keys

        return None

    def getCurrentLocationScenesNames(self):
        object_name = self.object.getName()
        map_data = Map2Manager.getMapData(object_name)
        locations = map_data.getLocations()

        current_location = self.getCurrentLocation()
        location_scenes = locations.get(current_location, None)

        if location_scenes is None:
            return []

        scene_names = []
        for scene_name, group_name, main in location_scenes:
            scene_names.append(scene_name)

        return scene_names

    def __playerPlacePrototypeTrigger(self, scene_name):
        check_scene_name = self.getCurrentLocation()
        current_location_scenes_names = self.getCurrentLocationScenesNames()

        if scene_name == check_scene_name:
            return True

        if SceneManager.isSpecialScene(check_scene_name):
            if scene_name == SceneManager.getSpecialMainSceneName(check_scene_name):
                return True

        if current_location_scenes_names is not None:
            if scene_name in current_location_scenes_names:
                if check_scene_name in current_location_scenes_names:
                    return True

        return False

    def _onPreparation(self):
        MapData = Map2Manager.getMapData(self.object.getName())

        self.all_done_scenes = Map2Manager.getAllDoneScenes()
        collection = MapData.getCollection()
        self.hog_collection = MapData.getHogCollection()

        movie_slots = self.object.getObject("Movie2_Slots")
        movie_slots.setEnable(True)
        movie_slots_entity = movie_slots.getEntity()

        locked_prototype_name = MapData.getLockedPrototypeName()
        blocked_prototype_name = MapData.getBlockedPrototypeName()
        player_place_complete_prototype_name = MapData.getPlayerPlaceCompletePrototypeName()
        player_place_prototype_name = MapData.getPlayerPlacePrototypeName()
        player_place_with_quests_prototype_name = MapData.getPlayerPlaceWithQuestsName()
        complete_prototype_name = MapData.getCompletePrototypeName()
        open_prototype_name = MapData.getOpenPrototypeName()
        all_done_prototype_name = MapData.getAllDonePrototypeName()
        special_prototype_name = MapData.getSpecialPrototypeName()

        custom_indicators_on_map = Mengine.getCurrentAccountSettingBool("DifficultyCustomIndicatorsOnMap")
        self._toggleIndicatorsPlate(custom_indicators_on_map)

        for scene_name, map_point in collection.iteritems():
            overview = map_point.getOverviewMovie()
            if overview is not None:
                overview.setEnable(False)
            slot_id = map_point.getSlotID()
            slot = movie_slots_entity.getMovieSlot(slot_id)
            if scene_name not in self.OpenScenes:
                if locked_prototype_name is None:
                    continue
                self.generateMovie(locked_prototype_name, slot_id, slot)
                continue
            if scene_name in self.BlockedScenes:
                if blocked_prototype_name is None:
                    continue
                self.generateMovie(blocked_prototype_name, slot_id, slot)
                continue

            place_movie = None

            if custom_indicators_on_map is False:
                if open_prototype_name is not None:
                    place_movie = self.generateMovie(all_done_prototype_name, slot_id, slot)

            elif self.__playerPlacePrototypeTrigger(scene_name):
                if scene_name in self.CompletedScenes:
                    if player_place_complete_prototype_name is not None:
                        place_movie = self.generateMovie(player_place_complete_prototype_name, slot_id, slot)
                elif scene_name in self.all_done_scenes:
                    if player_place_prototype_name is not None:
                        place_movie = self.generateMovie(player_place_prototype_name, slot_id, slot)
                else:
                    if player_place_with_quests_prototype_name is not None:
                        place_movie = self.generateMovie(player_place_with_quests_prototype_name, slot_id, slot)
            else:
                if scene_name in self.CompletedScenes:
                    if complete_prototype_name is not None:
                        place_movie = self.generateMovie(complete_prototype_name, slot_id, slot)
                elif scene_name not in self.all_done_scenes:
                    if open_prototype_name is not None:
                        place_movie = self.generateMovie(open_prototype_name, slot_id, slot)
                else:
                    if all_done_prototype_name is not None:
                        place_movie = self.generateMovie(all_done_prototype_name, slot_id, slot)

            if place_movie is not None:
                place_movie_entity = place_movie.getEntity()
                if place_movie_entity.hasSocket("socket") is True:
                    self.sockets[place_movie] = scene_name

            has_special = map_point.getHasSpecial()
            if has_special is True:
                if special_prototype_name is not None:
                    self.generateMovie(special_prototype_name, slot_id, slot)

        for block_id in self.hog_collection.keys():
            hog_movie, open_hog_movie = self.hog_collection[block_id]
            open_hog_movie.setEnable(False)
            if block_id in self.OpenHog:
                hog_movie.setEnable(False)
            else:
                hog_movie.setEnable(True)
                hog_movie.setLoop(True)
                hog_movie.setPlay(True)

    def _toggleIndicatorsPlate(self, state):
        if DefaultManager.getDefaultBool("DefaultMapToggleIndicatorsPlate", False) is False:
            return

        def _setState(movie_name, enable):
            if self.object.hasObject(movie_name):
                movie = self.object.getObject(movie_name)
                movie.setEnable(enable)

        if state is True:
            _setState("Movie2_Indicators_On", True)
            _setState("Movie2_Indicators_Off", False)
        else:
            _setState("Movie2_Indicators_Off", True)
            _setState("Movie2_Indicators_On", False)

    def _scopeZoomEffectTransition(self, source, movie):
        current_scene = SceneManager.getCurrentScene()

        if current_scene is None:
            return

        main_layer = current_scene.getMainLayer()

        cur_scale = main_layer.getScale()

        scale_to = (cur_scale[0] * self.zoom_effect_zoom_factor, cur_scale[1] * self.zoom_effect_zoom_factor, cur_scale[2] * self.zoom_effect_zoom_factor,)

        movie_entity = movie.getEntity()
        socket = movie_entity.getSocket("socket")
        point = socket.getWorldPolygonCenter()

        with source.addFork() as fork:
            fork.addTask("TaskNodeSetPosition", Node=main_layer, Value=point)
            fork.addTask("TaskNodeSetOrigin", Node=main_layer, Value=point)
            fork.addTask("TaskNodeScaleTo", Node=main_layer, To=scale_to, Time=self.time_zoom_in)

    def __onMovieSocketEnter(self, source, movie_object, scene_name):
        EVENT_SHOW_OVERVIEW(movie_object, scene_name)

        map_data = Map2Manager.getMapData(self.object.getName())
        collection = map_data.getCollection()
        map_point_data = collection[scene_name]
        movie_overview = map_point_data.getOverviewMovie()

        current_location_scenes_names = self.getCurrentLocationScenesNames()

        if movie_overview is not None:
            source.addTask("TaskEnable", Object=movie_overview)
            source.addTask("TaskMovie2Play", Movie2=movie_overview, Wait=False, Loop=False)
            source.addTask("TaskMovie2Play", Movie2=movie_object, Wait=False)

        with source.addRaceTask(2) as (tc_click, tc_leave):
            tc_click.addTask("TaskMovie2SocketClick", Movie2=movie_object, Any=True)
            tc_click.addScope(self._scopeZoomEffectTransition, movie_object)
            if scene_name in current_location_scenes_names:
                current_scene = SceneManager.getCurrentGameSceneName()
                tc_click.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(current_scene,))
            else:
                tc_click.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(scene_name,))

            tc_leave.addScope(self._scopeLeaveOverview, movie_object)

        if movie_overview is not None:
            source.addTask("TaskMovie2Stop", Movie2=movie_overview)
            source.addTask("TaskMovieLastFrame", Movie=movie_overview, Value=False)
            source.addTask("TaskEnable", Object=movie_overview, Value=False)

        source.addFunction(EVENT_HIDE_OVERVIEW, movie_object, scene_name)

    def _scopeLeaveOverview(self, source, movie_object):
        if Mengine.hasTouchpad() is True:
            with source.addRaceTask(2) as (tc_another_overview, tc_miss_click):
                tc_another_overview.addEvent(EVENT_SHOW_OVERVIEW)
                tc_miss_click.addTask("TaskMouseButtonClick")
                tc_miss_click.addDelay(10.0)
        else:
            source.addTask("TaskMovie2SocketLeave", Movie2=movie_object, Any=True)

    def _scopeClickOverviewPoint(self, source, movie_object):
        if Mengine.hasTouchpad() is True:
            source.addTask("TaskMovie2SocketClick", Movie2=movie_object, Any=True)
        else:
            source.addTask("TaskMovie2SocketEnter", Movie2=movie_object, Any=True)

    # === Activate \ Deactivate ========================================================================================

    def _onActivate(self):
        for movie_object, scene_name in self.sockets.iteritems():
            movie_object_name = movie_object.getName()
            with TaskManager.createTaskChain(Name="MapPointOverView_%s" % (movie_object_name), Repeat=True) as source:
                source.addScope(self._scopeClickOverviewPoint, movie_object)
                source.addScope(self.__onMovieSocketEnter, movie_object, scene_name)

        for hog_id in self.PlayedOpenHog[:]:
            hog = self.hog_collection.get(hog_id)

            if hog is None:
                continue

            open_hog_movie = hog[1]

            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskEnable", Object=open_hog_movie)
                tc.addTask("TaskMovie2Play", Movie2=open_hog_movie, Wait=True, Loop=False)
                tc.addTask("TaskEnable", Object=open_hog_movie, Value=False)

        self.object.setParam("PlayedOpenHog", [])

    def _onDeactivate(self):
        Notification.notify(Notificator.onMapEntityDeactivate)
        for movie_object, scene_name in self.sockets.iteritems():
            movie_object_name = movie_object.getName()
            if TaskManager.existTaskChain("MapPointOverView_%s" % (movie_object_name)) is True:
                TaskManager.cancelTaskChain("MapPointOverView_%s" % (movie_object_name))

        self.sockets = {}
        for movie_object in self.movie_objects:
            movie_object.onDestroy()
        self.movie_objects = []
        self.all_done_scenes = []