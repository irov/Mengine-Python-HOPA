from Foundation.Manager import Manager

class SemaphoreManager(Manager):
    s_semaphore = {}

    onSessionSaveObserver = None
    onSessionLoadObserver = None

    @staticmethod
    def _onInitialize():
        return

    @staticmethod
    def _onFinalize():
        SemaphoreManager.s_semaphore = []

    @staticmethod
    def _onSave():
        dict_save = {}
        dict_save["Semaphores"] = {}

        for name, semaphore in SemaphoreManager.s_semaphore.iteritems():
            value = semaphore.getValue()
            dict_save["Semaphores"][name] = value

        return dict_save

    @staticmethod
    def _onLoad(dict_save):
        Semaphores = dict_save.get("Semaphores", None)

        if Semaphores is None:
            return

        for name, value in Semaphores.iteritems():
            semaphore = Semaphore(value, name)
            SemaphoreManager.s_semaphore[name] = semaphore

    @staticmethod
    def addSemaphore(semaphore):
        SemaphoreManager.s_semaphore[semaphore.event.name] = semaphore

    @staticmethod
    def getSemaphore(name):
        if name not in SemaphoreManager.s_semaphore:
            SemaphoreManager.s_semaphore[name] = Semaphore(None, name)

        semaphore = SemaphoreManager.s_semaphore[name]

        return semaphore