from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemNotebook(System):
    def __init__(self):
        super(SystemNotebook, self).__init__()
        self.Notebook = DemonManager.getDemon("Notebook")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTasksOpen, self.__onTasksOpen)
        self.addObserver(Notificator.onTasksClose, self.__onTasksClose)

        return True

    def _onStop(self):
        pass

    def __onTasksClose(self, NoteID):
        self.Notebook.appendParam("CloseNotes", NoteID)

        return False

    def __onTasksOpen(self, NoteID):
        self.Notebook.appendParam("OpenNotes", NoteID)
        self.Notebook.setParam("CurrentNote", NoteID)

        return False