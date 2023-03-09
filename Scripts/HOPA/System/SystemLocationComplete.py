from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.LocationCompleteManager import LocationCompleteManager
from HOPA.StageManager import StageManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


# if LocationCompleteManager has issues, then this filter will used
DEFAULT_QUEST_FILTER = ['Teleport', 'Play', 'Enable', 'Click', 'RunParagraph', 'WaitParagraph', 'TechnicalQuest']


class SystemLocationComplete(System):
    def _onParams(self, params):
        super(SystemLocationComplete, self)._onParams(params)

        self.DemonLocationComplete = None
        if DemonManager.hasDemon("LocationComplete"):
            self.DemonLocationComplete = DemonManager.getDemon("LocationComplete")

        self.__setLocationsData()

        self.quest_filter = DEFAULT_QUEST_FILTER
        if LocationCompleteManager.hasQuestTypeFilter() is True:
            self.quest_filter = LocationCompleteManager.getQuestTypeFilter()

    def __setLocationsData(self):
        """
        mg, hogs, dialog, cutscene, preintro, tasks is gamearea
        to avoid hardcoding game locations we took already hardcoded
        game locations from map 2 manager

        so because we ignore quest Teleport and Click, becouse of transitions
        we need to check MG and HO if they complete seperatly

        also there are several chapters, we will be fine if we append all chapters in one container

        :param self.locations_data = {
                    scene_name: [HO or MG name, ...], ...
                }
        """
        self.locations_data = dict()

        map_objects = Map2Manager.getAllMapData()
        for map_object in map_objects.values():
            map_object_collection = map_object.getCollection()

            for scene_name, map_point in map_object_collection.items():
                self.locations_data[scene_name] = map_point.getMinigames()

    def _onRun(self):
        self.addObserver(Notificator.onParagraphCompleteForReal, self.__cbCheckLocationComplete)
        self.addObserver(Notificator.onSceneInit, self.__cbCheckLocationComplete)
        self.addObserver(Notificator.onLocationComplete, self._cbLocationComplete)
        return True

    @staticmethod
    def __waitAndRunParagraphs(scene_paragraphs):
        run_and_wait_paragraphs = []
        for paragraph in scene_paragraphs:
            if paragraph.Status == 3:
                continue
            run_and_wait_paragraphs.append(paragraph)
        return run_and_wait_paragraphs

    @staticmethod
    def __cbQuestFilter(quest, quest_type_list, ignored_quests):
        quest_type = quest.questType
        if quest_type in ignored_quests:
            return
        if quest.complete:
            return
        quest_type_list.append(quest_type)

    def __sceneQuestsIsComplete(self, cur_stage, cur_scene_name):
        scenario_chapter = cur_stage.getScenarioChapter()
        scene_paragraphs = scenario_chapter.findAllSceneScenarioParagraphs(cur_scene_name)

        quest_type_list = []
        for paragraph in SystemLocationComplete.__waitAndRunParagraphs(scene_paragraphs):
            paragraph.visitQuests(SystemLocationComplete.__cbQuestFilter, False, quest_type_list, self.quest_filter)

        # def debugPrintParagraphsState():
        #     print '\n\nCURRENT SCENE NAME', cur_scene_name
        #     print 'len(scene_paragraphs) =', len(scene_paragraphs)
        #     paragraphs_states = {'Wait': 0, 'Run': 0, 'Complete': 0}
        #
        #     for paragraph in scene_paragraphs:
        #         if paragraph.Status == 1:
        #             paragraphs_states['Wait'] += 1
        #         elif paragraph.Status == 2:
        #             paragraphs_states['Run'] += 1
        #         elif paragraph.Status == 3:
        #             paragraphs_states['Complete'] += 1
        #         else:
        #             print '[ERROR] Unrecognized paragraph status(1-3)'
        #
        #     print 'paragraphs_states:\n', paragraphs_states
        #
        # debugPrintParagraphsState()
        #
        # def debugPrintQuestCounter():
        #     quest_type_counter = dict(
        #         (quest_type, quest_type_list.count(quest_type)) for quest_type in set(quest_type_list)
        #     )
        #     print 'quest of wait and run paragraphs:\n{}\n'.format(quest_type_counter)
        #
        # debugPrintQuestCounter()

        if len(quest_type_list) == 0:
            return True
        else:
            return False

    def __sceneMGisComplete(self, cur_scene_name):
        cur_scene_mg_list = self.locations_data.get(cur_scene_name, [])
        for enigma_name in cur_scene_mg_list:
            if not EnigmaManager.hasEnigma(enigma_name):
                continue

            enigma_obj = EnigmaManager.getEnigmaObject(enigma_name)
            if not enigma_obj.getComplete():
                return False
        return True

    def __cbCheckLocationComplete(self, *_, **__):
        cur_stage = StageManager.getCurrentStage()
        if cur_stage is None or cur_stage.getTag() is not "FX":
            return False

        cur_scene_name = SceneManager.getCurrentSceneName()

        if len(self.locations_data) > 0:
            if cur_scene_name not in self.locations_data:
                return False

        if not SceneManager.isGameScene(cur_scene_name) or not ZoomManager.sceneHasZooms(cur_scene_name):
            return False

        if self._isLocationComplete(cur_scene_name) is True:
            return False

        scene_mg_is_complete = self.__sceneMGisComplete(cur_scene_name)
        if not scene_mg_is_complete:
            return False

        quests_is_complete = self.__sceneQuestsIsComplete(cur_stage, cur_scene_name)

        if quests_is_complete:
            Notification.notify(Notificator.onLocationComplete, cur_scene_name)

        return False

    def _cbLocationComplete(self, scene_name):
        if self.DemonLocationComplete is None:
            return True

        self.DemonLocationComplete.appendParam("CompleteScenes", scene_name)
        return False

    def _isLocationComplete(self, scene_name):
        if self.DemonLocationComplete is not None:
            demon = self.DemonLocationComplete
            param = "CompleteScenes"
        else:
            demon = Map2Manager.getCurrentMapObject()
            param = "CompletedScenes"

        complete_scenes = demon.getParam(param)
        if scene_name in complete_scenes:
            return True

        return False
