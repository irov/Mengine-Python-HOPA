from Foundation.SystemManager import SystemManager
from Foundation.Utils import isCollectorEdition
from HOPA.Macro.MacroCommand import MacroCommand


class MacroCollectiblesTransitionPadlock(MacroCommand):
    def _onGenerate(self, source):
        if isCollectorEdition() is False:
            return

        if not SystemManager.hasSystem('SystemCollectibles'):
            return

        source.addScope(self._run)

    def _run(self, source):
        system_collectibles = SystemManager.getSystem('SystemCollectibles')
        collectible_group_param = system_collectibles.getCollectibleGroup(self.SceneName)

        if collectible_group_param is None:
            if _DEVELOPMENT is True:
                Trace.log("Macro", 0, "MacroCollectiblesTransitionPadlock: not exist collectibles on scene {!r}".format(self.SceneName))
            source.addDummy()
        else:
            collectible_group_param.transition_padlock = True
            source.addFunction(collectible_group_param.setTransitionPadlock, False)
