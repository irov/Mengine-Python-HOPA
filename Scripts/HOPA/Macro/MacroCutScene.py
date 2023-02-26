from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from HOPA.Macro.MacroCommand import MacroCommand

class MacroCutScene(MacroCommand):
    def _onValues(self, values):
        self.CutSceneID = values[0]
        self.NoBlinds = False
        if len(values) > 1:
            self.NoBlinds = True
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSceneEnter", SceneName=self.SceneName)

        MusicFadeCutScene = DefaultManager.getDefault("MusicFadeCutScene", 0.25)

        with GuardBlockMusicVolumeFade(source, "CutScene", MusicFadeCutScene) as source:
            source.addTask("TaskSceneLayerGroupEnable", LayerName="CutSceneBlinds", Value=True)
            source.addTask("TaskEnable", GroupName="CutSceneBlinds", ObjectName="Movie_Open", Value=False)
            if self.NoBlinds is False:
                source.addTask("TaskEnable", GroupName="CutSceneBlinds", ObjectName="Movie_Close", Value=True)
                source.addTask("TaskMoviePlay", GroupName="CutSceneBlinds", MovieName="Movie_Close", Wait=True)
                pass

            source.addTask("TaskSceneLayerGroupEnable", LayerName="CutScene_Interface", Value=True)

            source.addTask("TaskScenarioInjectionCreate", ScenarioID=self.CutSceneID, Skiped=True)

            with source.addRaceTask(2) as (tc_cutScene, tc_skip):
                tc_cutScene.addTask("TaskScenarioEnd", ScenarioID=self.CutSceneID)

                if GroupManager.hasObject("CutScene_Interface", "Button_Next") is True:
                    tc_skip.addTask("TaskEnable", GroupName="CutScene_Interface", ObjectName="Button_Next", Value=False)
                    pass
                tc_skip.addTask("TaskButtonClick", GroupName="CutScene_Interface", ButtonName="Button_Skip")
                tc_skip.addTask("TaskScenarioSkip", ScenarioID=self.CutSceneID)
                if GroupManager.hasObject("CutScene_Interface", "Button_Next") is True:
                    tc_skip.addTask("TaskEnable", GroupName="CutScene_Interface", ObjectName="Button_Next", Value=True)
                    pass
                pass

            source.addTask("TaskSceneLayerGroupEnable", LayerName="CutScene_Interface", Value=False)

            source.addTask("TaskEnable", GroupName="CutSceneBlinds", ObjectName="Movie_Close", Value=False)
            if self.NoBlinds is False:
                source.addTask("TaskEnable", GroupName="CutSceneBlinds", ObjectName="Movie_Open", Value=True)
                source.addTask("TaskMoviePlay", GroupName="CutSceneBlinds", MovieName="Movie_Open", Wait=True)
                pass

            source.addTask("TaskSceneLayerGroupEnable", LayerName="CutSceneBlinds", Value=False)
            pass
        pass
    pass