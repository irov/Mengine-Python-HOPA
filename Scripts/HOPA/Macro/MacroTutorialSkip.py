from Foundation.SystemManager import SystemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroTutorialSkip(MacroCommand):
    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        def __isTutorialAlreadySkip(isSkip, cb):
            SystemDifficulty = SystemManager.getSystem("SystemDifficulty")

            if SystemDifficulty.isTutorialSkip() is True:
                cb(isSkip, 0)
            else:
                cb(isSkip, 1)
                pass
            pass

        with source.addSwitchTask(2, __isTutorialAlreadySkip) as (source_ok, source_wait):
            source_wait.addTask("TaskListener", ID=Notificator.onTutorialSkip)
            pass
        pass
