from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.System.SystemCollectibles import SystemCollectibles


class MacroCollectiblesVisitScene(MacroCommand):
    """
        Macro for manual set current scene_visited to True
    """

    def _visitScene(self):
        scene_name = self.SceneName
        if scene_name in SystemCollectibles.s_collectibles_groups:
            SystemCollectibles.s_collectibles_groups[scene_name].scene_visited = True

    def _onGenerate(self, source):
        source.addFunction(self._visitScene)
