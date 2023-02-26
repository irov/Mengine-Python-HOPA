from Foundation.TaskManager import TaskManager
from Notification import Notification

class StorePageBaseComponent(object):

    def __init__(self, page):
        self.page = page
        self.object = page.object
        self._observers = []
        self._tcs = []

        self.__in_run = False
        self.__check_failed = False

    def _check(self):
        return True

    def run(self):
        if self.isRun() is True:
            Trace.log("Entity", 0, "{}::run is already run".format(self.__class__.__name__))
            return

        if self._check() is False:
            self.__setCheckFailedState(True)
            return

        self._run()

        self.__setRunState(True)

    def _run(self):
        pass

    def cleanUp(self):
        for observer in self._observers:
            Notification.removeObserver(observer)
        self._observers = None

        for tc in self._tcs:
            tc.cancel()
        self._tcs = None

        self._cleanUp()
        self.page = None
        self.object = None

    def _cleanUp(self):
        pass

    def stop(self):
        if self.isRun() is False:
            if self.isCheckFailed() is True:
                Trace.msg_err("{}::stop got an error during startup (in `run`)")
                return

            Trace.log("Entity", 0, "{}::stop is not run".format(self.__class__.__name__))
            return

        self.cleanUp()
        self._stop()

        self.__setRunState(False)

    def _stop(self):
        pass

    # utils

    def createTaskChain(self, Name, **params):
        tc_name = self.__class__.__name__ + "_" + Name
        tc = TaskManager.createTaskChain(Name=tc_name, **params)

        if tc is None:
            # wrong Name
            return

        self._tcs.append(tc)
        return tc

    def addObserver(self, notificator, fn, *args, **kwargs):
        observer = Notification.addObserver(notificator, fn, *args, **kwargs)
        self._observers.append(observer)

    def __setRunState(self, state):
        self.__in_run = state

    def isRun(self):
        return self.__in_run is True

    def __setCheckFailedState(self, state):
        self.__check_failed = state

    def isCheckFailed(self):
        return self.__check_failed is True