from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemGuidebook(System):
    def __init__(self):
        super(SystemGuidebook, self).__init__()
        self.onGuidebookAddPage = None
        pass

    def _onRun(self):
        self.onGuidebookAddPage = Notification.addObserver(Notificator.onGuidebookAddPage, self.__onGuideAdd)
        return True
        pass

    def __onGuideAdd(self, journalID):
        Guidebook = DemonManager.getDemon("Guidebook")
        Guidebook.appendParam("OpenPages", journalID)
        return False
        pass

    def _onStop(self):
        Notification.removeObserver(self.onGuidebookAddPage)
        pass

    pass
