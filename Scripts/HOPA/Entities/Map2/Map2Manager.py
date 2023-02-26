import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from HOPA.QuestManager import QuestManager
from HOPA.System.SystemItemCollect import SystemItemCollect
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

class MapData(object):
    def __init__(self, locked, open, all_done, complete, special, here, here_with_quest, here_complete, blocked, collection, hog_collection, locations):
        self.locked = locked
        self.open = open
        self.all_done = all_done
        self.complete = complete
        self.special = special
        self.here = here
        self.here_with_quest = here_with_quest
        self.here_complete = here_complete
        self.blocked = blocked
        self.collection = collection
        self.hog_collection = hog_collection
        self.locations = locations

    def getLockedPrototypeName(self):
        return self.locked

    def getOpenPrototypeName(self):
        return self.open

    def getAllDonePrototypeName(self):
        return self.all_done

    def getCompletePrototypeName(self):
        return self.complete

    def getSpecialPrototypeName(self):
        return self.special

    def getPlayerPlacePrototypeName(self):
        return self.here

    def getPlayerPlaceWithQuestsName(self):
        return self.here_with_quest

    def getPlayerPlaceCompletePrototypeName(self):
        return self.here_complete

    def getBlockedPrototypeName(self):
        return self.blocked

    def getCollection(self):
        return self.collection

    def getHogCollection(self):
        return self.hog_collection

    def getLocations(self):
        return self.locations

class MapPointData(object):
    def __init__(self, slot_id, has_special, overview, minigames):
        self.slot_id = str(slot_id)
        self.has_special = has_special
        self.overview = overview
        self.minigames = minigames

    def getSlotID(self):
        return self.slot_id

    def getHasSpecial(self):
        return self.has_special

    def getOverviewMovie(self):
        return self.overview

    def getMinigames(self):
        return self.minigames

class Map2Manager(object):
    s_objects = {}
    s_current_map = None
    s_map_objects = {}
    s_macro_type_filter = []
    s_map_scenes = {}
    s_open_scenes = []
    s_all_done_scenes = []

    @staticmethod
    def onFinalize():
        Map2Manager.s_objects = {}
        Map2Manager.s_current_map = None
        Map2Manager.s_map_objects = {}
        Map2Manager.s_map_scenes = {}
        Map2Manager.s_macro_type_filter = []

    @staticmethod
    def loadMacroTypeFilter(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            command_name = record.get("CommandName")
            Map2Manager.s_macro_type_filter.append(command_name)

        return True

    @staticmethod
    def getMacroTypeFilter():
        if len(Map2Manager.s_macro_type_filter) == 0:
            return None

        return Map2Manager.s_macro_type_filter

    @staticmethod
    def loadParams(module, param):
        if param == "Map":
            return Map2Manager.loadMapData(module, "Map")

        if param == "MapMacroTypeFilter":
            return Map2Manager.loadMacroTypeFilter(module, "MapMacroTypeFilter")

        return False

    @staticmethod
    def loadMapData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for value in records:
            """
            Map\Map.xlsx:
            DemonName	GroupName	SceneName	LockedPrototype OpenPrototype   
            CompletePrototype   AllDonePrototype    SpecialPrototype    HerePrototype   HereWithQuest   
            HereComplete    BlockedPrototype    Collection  HogCollection   MapLocation
            """

            demon_name = value.get("DemonName")
            group_name = value.get("GroupName")
            scene_name = value.get("SceneName")
            locked_prototype = value.get("LockedPrototype")
            open_prototype = value.get("OpenPrototype")
            complete_prototype = value.get("CompletePrototype")
            all_done_prototype = value.get("AllDonePrototype")
            special_prototype = value.get("SpecialPrototype")
            here_prototype = value.get("HerePrototype")
            here_with_quest_prototype = value.get("HereWithQuest")
            here_complete_prototype = value.get("HereComplete")
            blocked_prototype = value.get("BlockedPrototype")
            collection_name = value.get("Collection")
            hog_collection_name = value.get("HogCollection")
            map_location = value.get("MapLocation")

            if isinstance(GroupManager.getGroup(group_name), GroupManager.EmptyGroup):
                continue

            map_object = GroupManager.getObject(group_name, demon_name)

            hog_collection = None
            if hog_collection_name is not None:
                hog_collection = Map2Manager.loadHogCollection(module, hog_collection_name, map_object)

            locations = Map2Manager.loadMapLocation(module, map_location)
            s_collection = Map2Manager.loadMapCollection(module, collection_name, map_object)

            data = MapData(locked_prototype, open_prototype, all_done_prototype, complete_prototype, special_prototype, here_prototype, here_with_quest_prototype, here_complete_prototype, blocked_prototype, s_collection, hog_collection, locations)

            Map2Manager.s_map_objects[demon_name] = map_object

            Map2Manager.s_objects[demon_name] = data

            Map2Manager.s_map_scenes[demon_name] = scene_name

        return True

    @staticmethod
    def loadMapLocation(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        locations = {}

        for record in records:
            """
            Map\MapLocation.xlsx:
            Location    SceneName   GroupName   Main
            """

            location = record.get("Location")
            scene_name = record.get("SceneName")
            group_name = record.get("GroupName")
            main = record.get("Main")

            arr = locations.setdefault(location, [])
            arr.append((scene_name, group_name, main))

        return locations

    @staticmethod
    def loadHogCollection(module, name, map_object):
        records = DatabaseManager.getDatabaseRecords(module, name)
        data = {}

        for value in records:
            """
            Map\MapHogCollection.xlsx
            HogID   IdleMovie   OpenMovie
            """

            id = value.get("HogID")
            idle_movie_name = value.get("IdleMovie")
            open_movie_name = value.get("OpenMovie")
            idle_movie = map_object.getObject(idle_movie_name)
            open_movie = map_object.getObject(open_movie_name)

            data[id] = (idle_movie, open_movie)

        return data

    @staticmethod
    def loadMapCollection(module, name, map_object):
        data = {}

        def getMinigameList(minigame_number):
            minigame_list = []
            for iter_number in range(minigame_number):
                minigame_index = "MG{}".format(iter_number + 1)
                minigame = value.get(minigame_index, None)
                if minigame is not None:
                    minigame_list.append(minigame)
            return minigame_list

        records = DatabaseManager.getDatabaseRecords(module, name)

        for value in records:
            """
            Map\MapCollection.xlsx
            SceneName   Slot    hasSpecial  OverViewMovieName
            MG1 MG2 MG3 MG4
            """
            MAX_MINIGAMES = 4
            scene_name = value.get("SceneName")
            slot = value.get("Slot")
            has_special = bool(value.get("hasSpecial", 0))
            over_view_movie_name = value.get("OverViewMovieName")

            minigame_list = getMinigameList(MAX_MINIGAMES)

            overview = None
            if over_view_movie_name is not None:
                overview = map_object.getObject(over_view_movie_name)

            map_point = MapPointData(slot, has_special, overview, minigame_list)
            data[scene_name] = map_point

        return data

    @staticmethod
    def setCurrentMap(value):
        Map2Manager.s_current_map = value

    @staticmethod
    def getCurrentMap():
        return Map2Manager.s_current_map

    @staticmethod
    def getMapData(map_id):
        if Map2Manager.hasMapData(map_id) is False:
            return None

        record = Map2Manager.s_objects[map_id]
        return record

    @staticmethod
    def hasMapData(map_id):
        if map_id not in Map2Manager.s_objects:
            Trace.log("Map2Manager", 0, "Map2Manager.hasMapData invalid mapID %s" % (map_id))
            return False

        return True

    @staticmethod
    def getAllMapData():
        return Map2Manager.s_objects

    @staticmethod
    def getCurrentMapCollection():
        if Map2Manager.s_current_map is None:
            return None

        data = Map2Manager.s_objects[Map2Manager.s_current_map]
        collection = data.getCollection()

        return collection

    @staticmethod
    def getCurrentMapObject():
        if Map2Manager.s_current_map is None:
            return None

        object = Map2Manager.s_map_objects[Map2Manager.s_current_map]
        return object

    @staticmethod
    def hasCurrentMapObject():
        if Map2Manager.s_current_map is None:
            return False

        return True

    @staticmethod
    def getCurrentMapSceneName():
        if Map2Manager.s_current_map is None:
            return None

        scene_name = Map2Manager.s_map_scenes[Map2Manager.s_current_map]
        return scene_name

    @staticmethod
    def AllScenesIsDone():
        """
        if there are no quest's in all scenes we can tell this chapter is done
        """
        Map2Manager.s_all_done_scenes = Map2Manager.getAllDoneScenes()

        for elem in Map2Manager.s_open_scenes:
            if elem not in Map2Manager.s_all_done_scenes:
                return False
        return True

    @staticmethod
    def getAllDoneScenes():
        """
        this function return scenes with no quest we can complete
        this not necessary mean location is complete
        """
        all_done_scenes = list()
        current_map = Map2Manager.getCurrentMap()
        if current_map is None:
            return all_done_scenes

        map_data = Map2Manager.getMapData(current_map)
        collection = map_data.getCollection()
        locations = map_data.getLocations()

        for loc, scenes in locations.iteritems():
            if loc not in Map2Manager.s_open_scenes:
                continue

            quest_active = False

            for scene_name, group_name, main in scenes:
                if main != 1:
                    main_scene = None
                    for scene_name_in, group_name_in, main_in in scenes:
                        if main_in == 1:
                            main_scene = scene_name_in
                            break

                    if main_scene is None:
                        Trace.trace()
                        continue

                    transition_object = TransitionManager.findTransitionObjectToScene(main_scene, scene_name)
                    if transition_object is None:
                        continue

                item_collects = SystemItemCollect.getItemList()
                for (item_collect_scene_name, socket_name), (item_list, socket, flag) in item_collects.iteritems():
                    if scene_name != item_collect_scene_name:
                        continue
                    if flag is True:
                        continue

                    quest_active = True
                    break

                if SceneManager.hasSceneZooms(scene_name) is True:
                    zooms = SceneManager.getSceneZooms(scene_name)
                    for zoom_group_name in zooms:
                        if ZoomManager.hasZoom(zoom_group_name) is False:
                            continue

                        zoom_object = ZoomManager.getZoomObject(zoom_group_name)

                        if zoom_object.getEnable() is False or zoom_object.isInteractive() is False:
                            continue

                        has_scene_active_quest = QuestManager.hasAroundSceneQuest(scene_name, zoom_group_name)
                        if has_scene_active_quest is True:
                            quest_active = True
                            break
                        else:
                            pass

                has_active_quest = QuestManager.hasAroundSceneQuest(scene_name, group_name)
                if has_active_quest is True:
                    all_quests = QuestManager.getSceneQuests(scene_name, group_name)
                    for quest_m in all_quests:
                        if quest_m.isTechnical is True:
                            break
                        else:
                            quest_active = True
                            break

                else:
                    for minigame in collection[scene_name].getMinigames():
                        if minigame is None:
                            continue

                        group_mg_name = minigame

                        has_scene_active_quest = QuestManager.hasAroundSceneQuest(minigame, group_mg_name)
                        if has_scene_active_quest is True:
                            quests_minigames = QuestManager.getSceneQuests(minigame, group_mg_name)
                            for _ in quests_minigames:
                                transition_object = TransitionManager.findTransitionObjectToScene(scene_name, minigame)
                                if transition_object is not None:
                                    quest_active = True
                                    break

            if quest_active is False:
                all_done_scenes.append(loc)

        return all_done_scenes