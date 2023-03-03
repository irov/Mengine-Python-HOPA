from Foundation.DemonManager import DemonManager
from Foundation.System import System
from HOPA.ChapterManager import ChapterManager


class SystemObjective(System):
    def __init__(self):
        super(SystemObjective, self).__init__()

        self.DemonObjective = None
        pass

    def _onRun(self):
        self.DemonObjective = DemonManager.getDemon("Objectives")

        self.addObserver(Notificator.onObjectiveActivate, self.__onObjectiveActivate)
        self.addObserver(Notificator.onParagraphComplete, self.__onParagraphComplete)
        pass

    def _onStop(self):
        pass

    def __onObjectiveActivate(self, objectiveID, notifies):
        self.DemonObjective.appendParam("ObjectivesList", (objectiveID, notifies))

        return False
        pass

    def __onParagraphComplete(self, paragraphID):
        self._checkCompleteObjective()

        return False
        pass

    def __removeObjective(self, objectiveID, notifies):
        self.DemonObjective.delParam("ObjectivesList", (objectiveID, notifies))
        pass

    def __testParagraph(self, paragraphs):
        currentScenarioChapter = ChapterManager.getCurrentChapter()

        for paragraph in paragraphs:
            if currentScenarioChapter.isParagraphComplete(paragraph) is False:
                return False
                pass
            pass

        return True
        pass

    def _checkCompleteObjective(self):
        for objectiveID, notifies in self.DemonObjective.getObjectivesList():
            if self.__testParagraph(notifies) is False:
                continue
                pass

            self.__removeObjective(objectiveID, notifies)
            pass

        return False
        pass
