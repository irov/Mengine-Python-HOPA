from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemNotebookInventoryList(System):
    def __init__(self):
        super(SystemNotebookInventoryList, self).__init__()
        self.NotebookInventoryList = DemonManager.getDemon("NotebookInventoryList")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTasksOpen, self.__onTasksOpen)
        self.addObserver(Notificator.onTasksClose, self.__onTasksClose)

        return True
        pass

    def _onStop(self):
        pass

    def __onTasksClose(self, NoteID):
        openNotes = self.NotebookInventoryList.getOpenNotes()
        if NoteID not in openNotes:
            return False
            pass

        self.NotebookInventoryList.delParam("OpenNotes", NoteID)
        return False
        pass

    def __onTasksOpen(self, NoteID):
        self.NotebookInventoryList.appendParam("OpenNotes", NoteID)
        return False
        pass

    pass