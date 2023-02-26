from Foundation.ArrowManager import ArrowManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ChapterManager import ChapterManager
from HOPA.QuestManager import QuestManager
from HOPA.TipManager import TipManager
from Notification import Notification

class SystemTip(System):
    def __init__(self):
        super(SystemTip, self).__init__()
        self.activeTips = []
        self.objects = []
        self.listTypes = [Notificator.onSocketClick, Notificator.onItemClick, Notificator.onZoomClick, Notificator.onTransitionClick]

    def _onRun(self):
        for type in self.listTypes:
            self.addObserver(type, self.__onObjectClick)

        self.addObserver(Notificator.onTipActivate, self.__onActivateTip)
        self.addObserver(Notificator.onParagraphComplete, self.__onParagraphComplete)
        self.addObserver(Notificator.onTipActivateWithoutParagraphs, self.__onActivateTipWithoutParagraphs)
        self.addObserver(Notificator.onTipRemoveWithoutParagraphs, self.__onTipRemoveWithoutParagraph)

        for tip in self.activeTips:
            self.__startTip(tip)

        return True

    def _onSave(self):
        saveData = []
        for Tip in self.activeTips:
            saveData.append([Tip.object, Tip.notifies, Tip.tipID])

        return saveData

    def _onLoad(self, data_save):
        for tempTip in data_save:
            object, notifies, tipID = tempTip
            tip = TipManager.createTip(object, notifies, tipID)

            self.activeTips.append(tip)

            self.__startTip(tip)

        return False

    def _onStop(self):
        self.activeTips = []
        self.objects = []

    def __activateTip(self, object, tipID, notifies):
        Tip = TipManager.createTip(object, notifies, tipID)

        self.activeTips.append(Tip)

        Tip.object.setParamInteractive(True)

        self.__startTip(Tip)

    def __onActivateTip(self, object, tipID, notifies):
        if self.__testParagraph(notifies) is True:
            return False

        self.__activateTip(object, tipID, notifies)

        return False

    def __onActivateTipWithoutParagraphs(self, object, tipID):
        if TipManager.hasTip(tipID):
            self.__onTipRemoveWithoutParagraph(tipID)

        self.__activateTip(object, tipID, [])

        return False

    def __onTipRemoveWithoutParagraph(self, tipID):
        for tip in self.activeTips[:]:
            if tip.tipID == tipID:
                if tip.notifies:
                    Trace.log("System", 0, "SysteTip: __onTipRemoveWithoutParagraph try to remove tip with paragraphs!!!")
                else:
                    self.__removeTipObject(False, tip.object, tip)

                break

        return False

    def __testParagraph(self, paragraphs):
        currentScenarioChapter = ChapterManager.getCurrentChapter()

        for paragraph in paragraphs:
            if currentScenarioChapter.isParagraphComplete(paragraph) is False:
                return False

        return True

    def __onParagraphComplete(self, paragraphID):
        for tip in self.activeTips[:]:
            if not tip.notifies:
                continue

            if self.__testParagraph(tip.notifies) is False:
                continue

            self.__removeTipObject(False, tip.object, tip)

        return False

    def __onObjectClick(self, clickObject):
        if ArrowManager.emptyArrowAttach() is False:
            return False

        if clickObject not in self.objects:
            return False

        for tip in self.activeTips:
            if tip.object != clickObject:
                continue

            currentTip = tip

        if currentTip is None:
            Trace.log("System", 0, "SystemTip._onObjectClick: Error, %s in objects but not in activeTips!!!" % (clickObject.getName()))
            return False

        Notification.notify(Notificator.onBlackBarRelease, currentTip.tipID)
        Notification.notify(Notificator.onTipShow, currentTip.tipID)

        return False

    def __startTip(self, Tip):
        self.objects.append(Tip.object)

        QuestManager.appendActiveTipObjects(Tip.object)

    def __removeTipObject(self, isSkip, object, tip):
        object.setParamInteractive(False)

        self.activeTips.remove(tip)
        self.objects.remove(object)

        if TaskManager.existTaskChain("TipPlay"):
            Notification.notify(Notificator.onBlackBarRelease, tip.tipID)

        QuestManager.removeActiveTipObjects(object)