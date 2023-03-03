from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ChapterManager import ChapterManager
from HOPA.HintManager import HintManager


class SystemHintSceneExceptions(System):
    def __init__(self):
        super(SystemHintSceneExceptions, self).__init__()
        self.activeExceptions = {}
        pass

    def _onRun(self):
        self.addObserver(Notificator.onHintSceneException, self.__onHintSceneException)

        return True
        pass

    def _onSave(self):
        return self.activeExceptions
        pass

    def _onLoad(self, data_save):
        self.activeExceptions = data_save
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("HintSceneExceptions") is True:
            TaskManager.cancelTaskChain("HintSceneExceptions")
            pass

        self.activeExceptions = {}
        pass

    def __onHintSceneException(self, exceptionId, sceneName, groupName, notifies):
        self.activeExceptions[sceneName] = [exceptionId, notifies, groupName]
        return False
        pass

    def hasActiveException(self, curSceneName, curGroupName):
        for sceneName, value in self.activeExceptions.items():
            if curSceneName == sceneName:
                exceptionId, notifies, groupName = value
                if groupName != curGroupName:
                    continue
                    pass
                NotifiesSize = len(notifies)
                currentScenarioChapter = ChapterManager.getCurrentChapter()

                completeParagraphs = 0
                for ParagraphID in notifies:
                    completeParagraph = currentScenarioChapter.isParagraphComplete(ParagraphID)
                    if completeParagraph is False:
                        continue
                        pass
                    completeParagraphs += 1
                    pass

                if NotifiesSize == completeParagraphs:
                    del self.activeExceptions[sceneName]
                    return False
                    pass

                return True
                pass
            pass

        return False
        pass

    def showMind(self, curSceneName, curGroupName):
        if TaskManager.existTaskChain("HintSceneExceptions") is True:
            TaskManager.cancelTaskChain("HintSceneExceptions")
            pass

        for sceneName, value in self.activeExceptions.items():
            exceptionId, notifies, groupName = value
            if curSceneName == sceneName:
                if groupName != curGroupName:
                    continue
                    pass
                break
                pass
            pass

        MindID = HintManager.getSceneExceptionMindID(exceptionId)

        with TaskManager.createTaskChain(Name="HintSceneExceptions") as tc:
            tc.addTask("AliasMindPlay", MindID=MindID)
            pass
        pass

    pass
