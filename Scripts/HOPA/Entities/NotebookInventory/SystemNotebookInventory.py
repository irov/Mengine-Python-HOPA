from Foundation.DemonManager import DemonManager
from Foundation.System import System


class SystemNotebookInventory(System):
    def __init__(self):
        super(SystemNotebookInventory, self).__init__()
        self.NotebookInventory = DemonManager.getDemon("NotebookInventory")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTasksOpen, self.__onTasksOpen)
        self.addObserver(Notificator.onTasksClose, self.__onTasksClose)

        return True
        pass

    def _onStop(self):
        pass

    def __onTasksClose(self, NoteID):
        self.NotebookInventory.appendParam("CloseNotes", NoteID)

        return False
        pass

    def __onTasksOpen(self, NoteID):
        self.NotebookInventory.appendParam("OpenNotes", NoteID)

        return False
        pass

    pass
