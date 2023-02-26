from Foundation.DefaultManager import DefaultManager
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from HOPA.Macro.MacroCommand import MacroCommand

class MacroPlayCutSceneEx(MacroCommand):
    def _onValues(self, values):
        self.CutSceneDemonName = values[0]
        self.CutSceneSceneName = values[1]
        self.CutSceneName = values[2]
        pass

    def _onGenerate(self, source):
        MusicFadeCutScene = DefaultManager.getDefault("MusicFadeCutScene", 0.25)

        with GuardBlockMusicVolumeFade(source, "CutScene", MusicFadeCutScene) as source:
            source.addTask("TaskCutScenePlay", CutSceneDemonName=self.CutSceneDemonName, CutSceneSceneName=self.CutSceneSceneName, CutSceneName=self.CutSceneName)
            pass
        pass
    pass