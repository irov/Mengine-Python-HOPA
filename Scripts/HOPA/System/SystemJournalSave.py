from Foundation.DemonManager import DemonManager
from Foundation.System import System


class SystemJournalSave(System):
    def __init__(self):
        super(SystemJournalSave, self).__init__()

        self.Journal = DemonManager.getDemon("Journal")
        pass

    def _onSave(self):
        Pages = self.Journal.getParam("Pages")
        CurrentPage = self.Journal.getParam("CurrentPage")

        save_data = [Pages, CurrentPage]

        return save_data
        pass

    def _onLoad(self, data_save):
        Pages, CurrentPage = data_save

        self.Journal.setParam("Pages", Pages)
        self.Journal.setParam("CurrentPage", CurrentPage)
        pass

    def _onRun(self):
        return True
        pass

    def _onStop(self):
        self.Journal.setParam("Pages", [])
        self.Journal.setParam("CurrentPage", None)
