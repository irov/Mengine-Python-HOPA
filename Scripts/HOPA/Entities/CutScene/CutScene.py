from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.CutSceneManager import CutSceneManager
from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.ChapterSelectionManager import ChapterSelectionManager

REPLAY_TIME_DELAY = 5000.0


class CutScene(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "CutSceneName")
        Type.addAction(Type, "Play", Update=CutScene._updatePlay)
        Type.addAction(Type, "isFade")

    def __init__(self):
        super(CutScene, self).__init__()

        self.cut_scenes_list = None
        self.clean_scenes = []

    def _onDeactivate(self):
        self.__checkTaskChain()

    def _onActivate(self):
        if self.Play is True:
            return

        with TaskManager.createTaskChain(Name="CutSceneBlockProtector") as tc:
            with tc.addRaceTask(2) as (tc_ok, tc_replay):
                tc_ok.addListener(Notificator.onCutSceneStart)
                tc_ok.addPrint(" CUT SCENE OK")

                tc_replay.addDelay(REPLAY_TIME_DELAY)
                tc_replay.addPrint(" [!!] FOUND BLOCK: REPLAY PREVIOUS PARAGRAPH !!!!!!!")
                tc_replay.addFunction(self._safeLeaveScene)

    def _updatePlay(self, value):
        if value is True:
            self.__checkTaskChain()

            self.cut_scenes_list = self.__getMoveList(self.CutSceneName)

            self.__runTaskChain()

    def __runTaskChain(self):
        music_fade_cut_scene = DefaultManager.getDefault("MusicFadeCutScene", 0.25)
        current_scene_name = SceneManager.getCurrentSceneName()
        if current_scene_name is None:
            return

        cut_scene_skip = PolicyManager.getPolicy("CutSceneSkip", "PolicyCutSceneSkip")
        cut_scene_next = PolicyManager.getPolicy("CutSceneNext", "PolicyCutSceneNext")

        Notification.notify(Notificator.onCutSceneStart, self.CutSceneName)

        with TaskManager.createTaskChain(Name="runCutScene", Group=self.object, Cb=self.__cbPlayCutScene) as source:
            with GuardBlockMusicVolumeFade(source, "CutScene", music_fade_cut_scene) as tc:
                tc.addTask("TaskSceneInit", SceneAny=True)

                with tc.addRaceTask(2) as (tc_ok, tc_skip):
                    if self.isFade is True:
                        slot = SceneManager.getSceneDescription(current_scene_name)
                        if slot.hasSlotsGroup("Fade") is True:
                            fade_group_name = slot.getSlotsGroup("Fade")

                            tc_ok.addTask("AliasFadeOut", FadeGroupName=fade_group_name, Time=0.5 * 1000)  # speed fix

                    count = len(self.cut_scenes_list)
                    for index, scene in enumerate(self.cut_scenes_list):
                        movie_obj = CutSceneManager.getMovie(scene)
                        movie_text = CutSceneManager.getMovieText(scene)

                        with tc_ok.addRaceTask(3) as (tc_play, tc_text, tc_next):
                            tc_play.addTask("TaskEnable", Object=movie_obj)
                            tc_play.addTask("TaskFunction", Fn=self.__addToLayer, Args=(movie_obj, "CutScene_Movie",))
                            tc_play.addTask("TaskMoviePlay", Movie=movie_obj, Wait=True, ValidationGroupEnable=False)

                            if movie_text is not None:
                                tc_text.addTask("TaskEnable", Object=movie_text)
                                tc_text.addTask("TaskFunction", Fn=self.__addToLayer,
                                                Args=(movie_text, "CutScene_Movie_Text",))
                                tc_text.addTask("TaskMoviePlay", Movie=movie_text, Wait=True, ValidationGroupEnable=False)
                            else:
                                tc_text.addBlock()

                            if index + 1 != count:
                                tc_play.addTask("TaskEnable", Object=movie_obj, Value=False)

                            tc_next.addTask(cut_scene_next, CutSceneName=self.CutSceneName)
                            # tc_next.addTask("TaskFunction", Fn = self.__DisableNext, Args =(index,))
                            if index + 1 != count:
                                if self.isFade is True:
                                    slot = SceneManager.getSceneDescription(current_scene_name)
                                    if slot.hasSlotsGroup("Fade") is True:
                                        fade_group_name = slot.getSlotsGroup("Fade")
                                        tc_next.addTask("AliasFadeIn", FadeGroupName=fade_group_name,
                                                        Time=0.25 * 1000)  # speed fix

                                tc_next.addTask("TaskEnable", Object=movie_obj, Value=False)

                                if self.isFade is True:
                                    slot = SceneManager.getSceneDescription(current_scene_name)
                                    if slot.hasSlotsGroup("Fade") is True:
                                        fade_group_name = slot.getSlotsGroup("Fade")
                                        tc_next.addTask("AliasFadeOut", FadeGroupName=fade_group_name,
                                                        Time=0.25 * 1000)  # speed fix
                    tc_ok.addNotify(Notificator.onCutSceneComplete, self.CutSceneName)

                    tc_skip.addTask(cut_scene_skip, CutSceneName=self.CutSceneName)
                    tc_skip.addNotify(Notificator.onCutSceneSkip, self.CutSceneName)

                    if self.isFade is True:
                        slot = SceneManager.getSceneDescription(
                            current_scene_name)  # Take Fade group from default slots % by Sasha
                        if slot.hasSlotsGroup("Fade") is True:
                            fade_group_name = slot.getSlotsGroup("Fade")

                            tc_skip.addTask("AliasFadeIn", FadeGroupName=fade_group_name, Time=0.5 * 1000)  # speed fix

    def __cbPlayCutScene(self, is_skip):
        self._clearance()

        if is_skip is False:
            Notification.notify(Notificator.onCutScenePlay, self.CutSceneName, False)

    def _clearance(self):
        for movie in self.clean_scenes:
            movie.returnToParent()

        self.clean_scenes = []

        CutSceneManager.disableAll()

    def __checkTaskChain(self):
        if TaskManager.existTaskChain("CutSceneBlockProtector") is True:
            TaskManager.cancelTaskChain("CutSceneBlockProtector")
        if TaskManager.existTaskChain("runCutScene") is True:
            TaskManager.cancelTaskChain("runCutScene")

    def __addToLayer(self, movie_obj, layer_name):
        movie_obj.setEnable(True)
        self.clean_scenes.append(movie_obj)
        layer = SceneManager.getLayerScene(layer_name)
        movie_on_node = movie_obj.getEntityNode()
        layer.addChild(movie_on_node)

    def __getMoveList(self, cut_scene_start):
        list_ = []
        current_state = cut_scene_start

        while current_state is not None:
            if current_state in list_:
                Trace.log("Entity", 0, "CutSceneManager maybe recursive nextID in CutScenes")
                break
            list_.append(current_state)
            current_state = CutSceneManager.getNext(current_state)

        return list_

    # ----------- SAVE LEAVE CUT SCENE ---------------------------------------------------------------------------------

    def _safeLeaveScene(self):
        """ call this function to try leave cutscene when its blocked. Ways:
            CASE 1. Try to find previous paragraph by last CutScene name - and run it if possible
            CASE 2. Check if we have any open scenes - open map
            CASE 3. Try to run first chapter paragraph or scene
        """

        # CASE 1. Try to find previous paragraph by last CutScene name - and run it if possible
        # fixme: can't run with notify already done paragraph
        paragraph_id = CutSceneManager.findPreviousCutSceneParagraph(self.CutSceneName)
        if paragraph_id is not None:
            Trace.msg_dev("Found previous paragraph? id = " + str(paragraph_id) + " but can't run it - SKIP CASE 1")
            # self._forceRunParagraph(paragraph_id)
        #     return

        # CASE 2. Check if we have any open scenes - open map
        if Map2Manager.hasCurrentMapObject() is True and Map2Manager.hasOpenScenes() is True:
            Notification.notify(Notificator.onMapSilenceOpen)
            return

        # CASE 3.  Try to run first chapter paragraph or scene
        chapter = self._getValidChapterParams()
        if chapter is not None:
            # fixme: can't run with notify already done paragraph
            paragraph_id = chapter.start_paragraph
            if paragraph_id is not None:
                Trace.msg_dev("Found start chapter paragraph id = " + str(paragraph_id) + " but can't run it - SKIP")
            #     self._forceRunParagraph(paragraph_id)
            #     return

            if chapter.start_scene is not None:
                TaskManager.runAlias("AliasTransition", None, SceneName=chapter.start_scene)
                return

        Trace.log("Entity", 0, "CutScene impossible to find exit from this scene")

    def _forceRunParagraph(self, paragraph_id):
        # todo: check if paragraph is not complete - otherwise run it manually...
        Notification.notify(Notificator.onParagraphRun, paragraph_id)

    def _getValidChapterParams(self):
        chapter_name = ChapterSelectionManager.getCurrentChapter()
        if chapter_name is not None:
            chapter = ChapterSelectionManager.getChapterSelectionParam(chapter_name)
        else:
            chapter = ChapterSelectionManager.getFirstValidParam()

        if chapter is None:
            Trace.log("Entity", 0, "Not found any valid chapter params!!!!!")
            return None

        return chapter

