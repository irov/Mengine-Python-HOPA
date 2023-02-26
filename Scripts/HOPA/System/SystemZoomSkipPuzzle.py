from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager

class SystemZoomSkipPuzzle(System):
    BlackListEnigmaTypes = ["HOGRolling 564654654654645", ]

    def _onRun(self):
        self.addObserver(Notificator.onEnigmaActivate, self.__onEnigmaActivate)
        self.addObserver(Notificator.onEnigmaDeactivate, self.__onEnigmaDeactivate)

        self.addObserver(Notificator.onEnigmaStart, self.__onEnigmaPlay)
        self.addObserver(Notificator.onEnigmaRestore, self.__onEnigmaPlay)

        self.addObserver(Notificator.onEnigmaStop, self.__onEnigmaStop)
        self.addObserver(Notificator.onEnigmaPause, self.__onEnigmaStop)

        self.addObserver(Notificator.onChangeDifficulty, self.__onChangeDifficulty)

        return True
        pass

    def __onChangeDifficulty(self, _difficulty):
        skip_puzzle_demon = DemonManager.getDemon('SkipPuzzle')

        hint_active = DemonManager.getDemon('Hint').isActive()
        skip_puzzle_active = skip_puzzle_demon.isActive()
        skip_puzzle_enable = GroupManager.getGroup('SkipPuzzle').getEnable()

        if any([hint_active, not skip_puzzle_active, not skip_puzzle_enable]):
            return False

        entity_skip_puzzle = skip_puzzle_demon.getEntity()
        entity_skip_puzzle.runReloadSkipTC()

        return False

    def __onEnigmaActivate(self, enigma):
        EnigmaName = enigma.getEnigmaName()
        Enigma = EnigmaManager.getEnigma(EnigmaName)

        if Enigma is None:
            return False

        EnigmaObject = EnigmaManager.getEnigmaObject(EnigmaName)

        if EnigmaObject.getParam("Play") is False:
            return False

        Type = Enigma.getType()

        # print " <ZOOM SKIP PUZZLE> ENIGMA TYPE {}".format(Type)

        if Type in SystemZoomSkipPuzzle.BlackListEnigmaTypes:
            return False

        if Enigma.Skip is True:
            with TaskManager.createTaskChain() as tc:
                with tc.addRaceTask(2) as (race_0, race_1):
                    with race_0.addRaceTask(2) as (race_interrupt_0, race_interrupt_1):
                        race_interrupt_0.addListener(Notificator.onEnigmaDeactivate)
                        race_interrupt_1.addListener(Notificator.onEnigmaStop)

                    with race_1.addParallelTask(2) as (parallel_0, parallel_1):
                        parallel_0.addTask('TaskSceneLayerGroupEnable', LayerName='Hint', Value=False, WaitSceneInit=True)

                        parallel_1.addTask('TaskSceneLayerGroupEnable', LayerName='SkipZoomPuzzle', Value=True, WaitSceneInit=True)

        if Enigma.Reset is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='ResetMG', Value=True)

        return False

    def __onEnigmaDeactivate(self, enigma):
        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName is None:
            return False
        EnigmaName = enigma.getEnigmaName()
        Enigma = EnigmaManager.getEnigma(EnigmaName)

        if Enigma is None:
            return False

        EnigmaObject = EnigmaManager.getEnigmaObject(EnigmaName)

        if EnigmaObject.getParam("Play") is False:
            return False

        if Enigma.Skip is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='SkipZoomPuzzle', Value=False)
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='Hint', Value=True)

        if Enigma.Reset is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='ResetMG', Value=False)

        return False

    def __onEnigmaPlay(self, enigma):
        EnigmaName = enigma.getEnigmaName()
        Enigma = EnigmaManager.getEnigma(EnigmaName)

        if Enigma is None:
            return False

        Type = Enigma.getType()

        # print " <ZOOM SKIP PUZZLE> ENIGMA TYPE {}".format(Type)

        if Type in SystemZoomSkipPuzzle.BlackListEnigmaTypes:
            return False

        if Enigma.Skip is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='SkipZoomPuzzle', Value=True)
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='Hint', Value=False)

        if Enigma.Reset is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='ResetMG', Value=True)

        return False

    def __onEnigmaStop(self, enigma):
        currentSceneName = SceneManager.getCurrentSceneName()

        if currentSceneName is None:
            return False

        EnigmaName = enigma.getEnigmaName()
        Enigma = EnigmaManager.getEnigma(EnigmaName)

        if Enigma is None:
            return False

        if Enigma.Skip is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='SkipZoomPuzzle', Value=False)
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='Hint', Value=True)

        if Enigma.Reset is True:
            TaskManager.runAlias('TaskSceneLayerGroupEnable', None, LayerName='ResetMG', Value=False)

        return False