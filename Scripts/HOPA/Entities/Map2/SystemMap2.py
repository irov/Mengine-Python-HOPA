# coding=utf-8
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.Utils import isCollectorEdition
from HOPA.ChapterSelectionManager import ChapterSelectionManager
from HOPA.TransitionManager import TransitionManager

from Map2Manager import Map2Manager

class SystemMap2(System):
    s_dev_to_debug = False

    def __init__(self):
        super(SystemMap2, self).__init__()
        Map2Manager.s_open_scenes = []

    def _onRun(self):
        self.addObserver(Notificator.onSceneEnter, self.__cbSceneEnter)
        self.addObserver(Notificator.onMapPointBlock, self.__cbMapPointBlock)
        self.addObserver(Notificator.onMapPointUnblock, self.__cbMapPointUnblock)
        self.addObserver(Notificator.onMapHogUnblock, self.__cbMapHogUnblock)
        self.addObserver(Notificator.onLocationComplete, self.__cbLocationComplete)

        if isCollectorEdition() is True:
            self.__runTaskChain()
        else:
            self.__runTaskChainNoBonusMap()
        self.__cheatUnlockAllMap()

        if Mengine.hasTouchpad() is True:
            transition_back_button = GroupManager.getObject("Map", "Movie2Button_TransitionBack")
            transition_back_button.setEnable(False)

        return True

    @staticmethod
    def __cbLocationComplete(scene_name):
        if Map2Manager.hasCurrentMapObject() is False:
            return False

        current_map_object = Map2Manager.getCurrentMapObject()
        current_map_object.appendParam("CompletedScenes", scene_name)
        return False

    @staticmethod
    def __cbMapHogUnblock(hog_id):
        if Map2Manager.hasCurrentMapObject() is False:
            return False

        current_map_object = Map2Manager.getCurrentMapObject()

        current_map_object.appendParam("OpenHog", hog_id)
        current_map_object.appendParam("PlayedOpenHog", hog_id)
        return False

    @staticmethod
    def __cbSceneEnter(scene_name):
        if SceneManager.isCurrentGameScene() is False:
            return False

        current_map_collection = Map2Manager.getCurrentMapCollection()
        if current_map_collection is None:
            return False

        current_map_object = Map2Manager.getCurrentMapObject()
        open_scenes = current_map_object.getOpenScenes()

        if scene_name not in open_scenes:
            if scene_name in current_map_collection:
                Map2Manager.s_open_scenes.append(scene_name)
                current_map_object.appendParam("OpenScenes", scene_name)

        return False

    @staticmethod
    def __cbMapPointBlock(scene_name):
        if Map2Manager.hasCurrentMapObject() is False:
            return False

        current_map_object = Map2Manager.getCurrentMapObject()

        if scene_name not in current_map_object.getBlockedScenes():
            current_map_object.appendParam("BlockedScenes", scene_name)

        return False

    @staticmethod
    def __cbMapPointUnblock(scene_name):
        if Map2Manager.hasCurrentMapObject() is False:
            return False

        current_map_object = Map2Manager.getCurrentMapObject()
        if scene_name in current_map_object.getBlockedScenes():
            current_map_object.delParam("BlockedScenes", scene_name)

        return False

    @staticmethod
    def __scopeMapTransition(source):
        current_map_scene_name = ChapterSelectionManager.getCurrentMapSceneName()
        if current_map_scene_name is not None:
            source.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(current_map_scene_name, None, True))
        else:
            source.addTask("TaskDeadLock")

    @staticmethod
    def __scopeRaceMapOpenTask(source):
        with source.addRaceTask(2) as (race_thread_1, race_thread_2):
            # thread 1 if map scene transition was triggered not through click on "Movie2Button_Map"
            race_thread_1.addTask("TaskListener", ID=Notificator.onMapEntityInit)

            race_thread_2.addTask("TaskMovie2ButtonClick", GroupName="OpenMap", Movie2ButtonName="Movie2Button_Map")
            race_thread_2.addTask("TaskScope", Scope=SystemMap2.__scopeMapTransition)

    @staticmethod
    def __scopeRaceMapCloseTask(source):
        current_map_group_name = ChapterSelectionManager.getCurrentMapGroupName()

        with source.addRaceTask(3) as (race_thread_1, race_thread_2, race_thread_3):
            # thread 1 if map scene transition was triggered not through click on "Button_Exit" or "TransitionBack"
            race_thread_1.addTask("TaskListener", ID=Notificator.onMapEntityDeactivate)

            race_thread_2.addTask("TaskButtonClick", GroupName=current_map_group_name, ButtonName="Button_Exit")
            race_thread_2.addTask("TaskFunction", Fn=TransitionManager.changeToGameScene)

            if Mengine.hasTouchpad() is False:
                race_thread_3.addTask("TaskMovie2ButtonClick", GroupName=current_map_group_name, Movie2ButtonName="Movie2Button_TransitionBack")
                race_thread_3.addTask("TaskFunction", Fn=TransitionManager.changeToGameScene)
            else:
                race_thread_3.addBlock()

    def __runTaskChain(self):
        with self.createTaskChain(Name="OpenMap", Repeat=True) as tc:
            tc.addTask("TaskScope", Scope=SystemMap2.__scopeRaceMapOpenTask)
            tc.addTask("TaskNotify", ID=Notificator.onMapOpen)

            tc.addTask("TaskScope", Scope=SystemMap2.__scopeRaceMapCloseTask)
            tc.addTask("TaskNotify", ID=Notificator.onMapClose)

    def __runTaskChainNoBonusMap(self):
        with self.createTaskChain(Name="OpenMap", Repeat=True) as tc:
            with tc.addRaceTask(3) as (tc_map1, tc_map2, tc_map3):
                tc_map1.addTask("TaskMovie2ButtonClick", GroupName="OpenMap", Movie2ButtonName="Movie2Button_Map")
                tc_map1.addTask("TaskNotify", ID=Notificator.onMapOpen)
                tc_map1.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=("Map", None, True,))

                tc_map2.addTask("TaskButtonClick", GroupName="Map", ButtonName="Button_Exit")
                tc_map2.addTask("TaskNotify", ID=Notificator.onMapClose)
                tc_map2.addTask("TaskFunction", Fn=TransitionManager.changeToGameScene)

                if Mengine.hasTouchpad() is False:
                    tc_map3.addTask("TaskMovie2ButtonClick", GroupName="Map", Movie2ButtonName="Movie2Button_TransitionBack")
                    tc_map3.addTask("TaskNotify", ID=Notificator.onMapClose)
                    tc_map3.addTask("TaskFunction", Fn=TransitionManager.changeToGameScene)
                else:
                    tc_map3.addBlock()

    @staticmethod
    def getAllMapsOpenScenes():
        open_scenes = []
        for map_object in Map2Manager.s_map_objects.values():
            open_scenes += map_object.getOpenScenes()
        return open_scenes

    @staticmethod
    def _onSave():
        data_save = Map2Manager.s_open_scenes, Map2Manager.s_current_map
        return data_save

    @staticmethod
    def _onLoad(data_save):
        Map2Manager.s_open_scenes = data_save[0]
        Map2Manager.s_current_map = data_save[1]

    def __cheatUnlockAllMap(self):
        if Mengine.hasOption('cheats') is False:
            return

        def __unlockAllMap(widget=None):
            current_map_collection = Map2Manager.getCurrentMapCollection()
            if current_map_collection is None:
                return

            current_map_object = Map2Manager.getCurrentMapObject()
            map_data = Map2Manager.getMapData(Map2Manager.getCurrentMap())
            locations = map_data.getLocations()
            hog_collection = map_data.getHogCollection()
            open_scenes = current_map_object.getOpenScenes()

            for scene_name in locations.keys():
                if isinstance(scene_name, (list, tuple)):
                    scene_name = scene_name[1]

                if scene_name not in open_scenes:
                    if scene_name in current_map_collection:
                        Map2Manager.s_open_scenes.append(scene_name)
                        current_map_object.appendParam("OpenScenes", scene_name)

            for hog_id in hog_collection.keys():
                current_map_object.appendParam("OpenHog", hog_id)
                current_map_object.appendParam("PlayedOpenHog", hog_id)

            if widget is not None:
                widget.setHide(True)

            Trace.msg("<Cheats> Unlock all map points by cheats")

        def checkEditBox():
            if SystemManager.hasSystem("SystemEditBox"):
                system_edit_box = SystemManager.getSystem("SystemEditBox")
                if system_edit_box.hasActiveEditbox():
                    return False
            return True

        with self.createTaskChain("SystemMap2Cheat") as tc:
            tc.addTask("TaskKeyPress", Keys=[DefaultManager.getDefaultKey("CheatsUnlockAllMap", 'VK_U')])
            with tc.addIfTask(checkEditBox) as (tc_true, _):
                tc_true.addFunction(__unlockAllMap)

        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemMap2.s_dev_to_debug is True:
            return
        SystemMap2.s_dev_to_debug = True

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")
        widget = Mengine.createDevToDebugWidgetButton("unlock_all_map")
        widget.setTitle("Unlock all map points")
        widget.setClickEvent(__unlockAllMap, widget)
        tab.addWidget(widget)