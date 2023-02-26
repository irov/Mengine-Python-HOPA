from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Notification import Notification

class SystemNotebookDescription(System):
    def __init__(self):
        super(SystemNotebookDescription, self).__init__()
        self.NotebookDescription = DemonManager.getDemon("NotebookDescription")
        pass

    def _onRun(self):
        self.onNoteClickObserver = Notification.addObserver(Notificator.onNoteClick, self.__onNoteClickOpen)
        self.onTasksOpenObserver = Notification.addObserver(Notificator.onTasksOpen, self.__onTasksOpen)
        return True
        pass

    def _onStop(self):
        Notification.removeObserver(self.onNoteClickObserver)
        Notification.removeObserver(self.onTasksOpenObserver)
        pass

    def __onTasksOpen(self, NoteID):
        self.NotebookDescription.setParam("CurrentNote", NoteID)
        return False
        pass

    def __onNoteClickOpen(self, NoteID):
        self.NotebookDescription.setParam("CurrentNote", NoteID)
        return False
        pass

    pass