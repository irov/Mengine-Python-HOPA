from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.CutSceneManager import CutSceneManager
from Notification import Notification

class CutScene(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "CutSceneName")
        Type.addAction(Type, "Play", Update=CutScene._updatePlay)
        Type.addAction(Type, "isFade")

    def __init__(self):
        super(CutScene, self).__init__()

        self.skip_time = 2
        self.cut_scenes_list = None
        self.clean_scenes = []

    def _onDeactivate(self):
        self.__checkTaskChain()

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

        with TaskManager.createTaskChain(Name="runCutScene", Group=self.object, Cb=self.__cbPlayCutScene) as source:
            with GuardBlockMusicVolumeFade(source, "CutScene", music_fade_cut_scene) as tc:
                tc.addTask("TaskSceneInit", SceneAny=True)

                with tc.addRaceTask(2) as (tc_ok, tc_skip):
                    if self.isFade is True:
                        slot = SceneManager.getSceneDescription(current_scene_name)  # Take Fade group from default slots % by Sasha
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
                                tc_text.addTask("TaskFunction", Fn=self.__addToLayer, Args=(movie_text, "CutScene_Movie_Text",))
                                tc_text.addTask("TaskMoviePlay", Movie=movie_text, Wait=True, ValidationGroupEnable=False)
                            else:
                                tc_text.addBlock()

                            if index + 1 != count:
                                tc_play.addTask("TaskEnable", Object=movie_obj, Value=False)

                            tc_next.addTask(cut_scene_next, CutSceneName=self.CutSceneName)
                            # tc_next.addTask("TaskFunction", Fn = self.__DisableNext, Args =(index,))
                            if index + 1 != count:
                                if self.isFade is True:
                                    slot = SceneManager.getSceneDescription(current_scene_name)  # Take Fade group from default slots % by Sasha
                                    if slot.hasSlotsGroup("Fade") is True:
                                        fade_group_name = slot.getSlotsGroup("Fade")
                                        tc_next.addTask("AliasFadeIn", FadeGroupName=fade_group_name, Time=0.25 * 1000)  # speed fix

                                tc_next.addTask("TaskEnable", Object=movie_obj, Value=False)

                                if self.isFade is True:
                                    slot = SceneManager.getSceneDescription(current_scene_name)  # Take Fade group from default slots % by Sasha
                                    if slot.hasSlotsGroup("Fade") is True:
                                        fade_group_name = slot.getSlotsGroup("Fade")
                                        tc_next.addTask("AliasFadeOut", FadeGroupName=fade_group_name, Time=0.25 * 1000)  # speed fix

                    tc_skip.addTask(cut_scene_skip, CutSceneName=self.CutSceneName)

                    if self.isFade is True:
                        slot = SceneManager.getSceneDescription(current_scene_name)  # Take Fade group from default slots % by Sasha
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