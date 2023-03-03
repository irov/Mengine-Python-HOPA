from Foundation.System import System
from HOPA.SemaphoreManager import SemaphoreManager


class SystemSemaphore(System):
    def _onParams(self, params):
        super(SystemSemaphore, self)._onParams(params)

    def _onRun(self):
        return True

    def _onSave(self):
        dict_save = {
            "Semaphores": {}
        }
        for name, semaphore in SemaphoreManager.s_semaphore.iteritems():
            value = semaphore.getValue()
            dict_save["Semaphores"][name] = value

        return dict_save

    def _onLoad(self, data_save):
        # if _DEVELOPMENT is True:
        #     semaphores = data_save["gggg"]

        semaphores = data_save.get("Semaphores", None)

        if semaphores is None:
            return

        for name, value in semaphores.iteritems():
            semaphore = Semaphore(value, name)
            SemaphoreManager.s_semaphore[name] = semaphore
