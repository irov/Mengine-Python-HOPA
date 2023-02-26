from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.SemaphoreManager import SemaphoreManager

class MacroSetSemaphore(MacroCommand):
    def _onValues(self, values):
        self.Name = values[0]
        self.To = values[1]
        pass

    def _onGenerate(self, source):
        Semaphore = SemaphoreManager.getSemaphore(self.Name)

        source.addSemaphore(Semaphore, To=self.To)
        pass
    pass